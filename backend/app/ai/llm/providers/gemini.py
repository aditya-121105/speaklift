from typing import AsyncIterator, Iterator, Any

from app.ai.llm.providers import LLMProvider, LLMResponse
from app.ai.shared.exceptions import AIConfigurationError, AIValidationError, LLMProviderError, LLMRateLimitError
from app.core.config import settings
from app.ai.llm.prompts.base import Prompt

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

class GeminiProvider(LLMProvider):
    """
    Concrete implementation of the LLMProvider for Google Gemini.
    
    This provider is isolated from the Business Layer and consumes only
    centralized configuration and Prompt objects.
    """
    
    @property
    def provider_name(self) -> str:
        return "gemini"
        
    @property
    def model_name(self) -> str:
        return settings.GEMINI_DEFAULT_MODEL
        
    @property
    def supports_json_mode(self) -> bool:
        return True
        
    @property
    def supports_function_calling(self) -> bool:
        return True
        
    @property
    def supports_streaming(self) -> bool:
        return True
        
    @property
    def context_window(self) -> int:
        return 1_000_000

    @property
    def is_local(self) -> bool:
        return False

    def _prepare_request(
        self,
        prompt: Prompt,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> tuple[str | None, str, float, int]:
        
        if not isinstance(prompt, Prompt):
            raise AIValidationError("GeminiProvider requires exactly a Prompt aggregate.")
        
        if not settings.GEMINI_API_KEY:
            raise AIConfigurationError("GEMINI_API_KEY is not configured.")
            
        render_result = prompt.render()
        
        final_sys = render_result.system_prompt
        final_user = render_result.user_prompt
        
        if not final_user or not final_user.strip():
            raise AIValidationError("Prompt user text cannot be empty.")
            
        final_temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
        final_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_OUTPUT_TOKENS
        
        return final_sys, final_user, final_temp, final_tokens

    def complete(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        final_sys, final_user, final_temp, final_tokens = self._prepare_request(
            prompt, temperature, max_tokens
        )
        return self._execute_complete(final_sys, final_user, final_temp, final_tokens, json_mode)

    def stream(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        final_sys, final_user, final_temp, final_tokens = self._prepare_request(
            prompt, temperature, max_tokens
        )
        return self._execute_stream(final_sys, final_user, final_temp, final_tokens)

    async def acomplete(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        final_sys, final_user, final_temp, final_tokens = self._prepare_request(
            prompt, temperature, max_tokens
        )
        return await self._execute_acomplete(final_sys, final_user, final_temp, final_tokens, json_mode)

    async def astream(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        final_sys, final_user, final_temp, final_tokens = self._prepare_request(
            prompt, temperature, max_tokens
        )
        return self._execute_astream(final_sys, final_user, final_temp, final_tokens)

    # ------------------------------------------------------------------
    # Isolated Execution Boundaries
    # ------------------------------------------------------------------

    def _get_client(self) -> "genai.Client":
        if not HAS_SDK:
            raise AIConfigurationError("google-genai SDK is not installed.")
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    def _build_config(self, system_prompt: str | None, temperature: float, max_tokens: int, json_mode: bool) -> "types.GenerateContentConfig":
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

    def _handle_api_error(self, e: Exception) -> Exception:
        if isinstance(e, APIError):
            if e.code == 429:
                return LLMRateLimitError(f"Gemini API rate limit exceeded: {e.message}")
            return LLMProviderError(f"Gemini API error ({e.code}): {e.message}")
        return LLMProviderError(f"Unexpected Gemini provider error: {str(e)}")

    def _execute_complete(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> LLMResponse:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature, max_tokens, json_mode)
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            return LLMResponse(
                text=response.text or "",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.model_name,
                provider=self.provider_name,
            )
        except Exception as e:
            raise self._handle_api_error(e) from e

    def _execute_stream(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int
    ) -> Iterator[str]:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature, max_tokens, json_mode=False)
        try:
            response_stream = client.models.generate_content_stream(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise self._handle_api_error(e) from e

    async def _execute_acomplete(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> LLMResponse:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature, max_tokens, json_mode)
        try:
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            
            return LLMResponse(
                text=response.text or "",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.model_name,
                provider=self.provider_name,
            )
        except Exception as e:
            raise self._handle_api_error(e) from e

    async def _execute_astream(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature, max_tokens, json_mode=False)
        try:
            response_stream = await client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise self._handle_api_error(e) from e
