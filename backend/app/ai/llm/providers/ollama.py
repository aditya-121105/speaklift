import httpx
from typing import AsyncIterator, Iterator

from app.ai.llm.providers import LLMProvider, LLMResponse
from app.ai.shared.exceptions import AIConfigurationError, AIValidationError, LLMProviderError, LLMRateLimitError
from app.core.config import settings
from app.ai.llm.prompts.base import Prompt

try:
    import ollama
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

class OllamaProvider(LLMProvider):
    """
    Concrete implementation of the LLMProvider for a local Ollama server.
    
    This provider consumes only centralized configuration and Prompt objects.
    """
    
    @property
    def provider_name(self) -> str:
        return "ollama"
        
    @property
    def model_name(self) -> str:
        return settings.OLLAMA_DEFAULT_MODEL
        
    @property
    def supports_json_mode(self) -> bool:
        return True
        
    @property
    def supports_function_calling(self) -> bool:
        # Depends on the model, but usually local models have varying support. 
        # Standardizing on False unless explicitly using tools in Ollama.
        return False
        
    @property
    def supports_streaming(self) -> bool:
        return True
        
    @property
    def context_window(self) -> int:
        return 8192  # Typical default for local models like llama3
        
    @property
    def is_local(self) -> bool:
        return True
        
    def _prepare_request(
        self,
        prompt: Prompt,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> tuple[str | None, str, float, int]:
        
        if not HAS_SDK:
            raise AIConfigurationError("ollama SDK is not installed.")
            
        if not isinstance(prompt, Prompt):
            raise AIValidationError("OllamaProvider requires exactly a Prompt aggregate.")
            
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

    def _get_client(self) -> "ollama.Client":
        return ollama.Client(host=settings.OLLAMA_BASE_URL)

    def _get_async_client(self) -> "ollama.AsyncClient":
        return ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

    def _build_options(self, temperature: float, max_tokens: int) -> dict:
        return {
            "temperature": temperature,
            "num_predict": max_tokens,
        }

    def _handle_api_error(self, e: Exception) -> Exception:
        if isinstance(e, ollama.ResponseError):
            if e.status_code == 429:
                return LLMRateLimitError(f"Ollama rate limit exceeded: {e.error}")
            return LLMProviderError(f"Ollama API error ({e.status_code}): {e.error}")
        elif isinstance(e, httpx.RequestError):
            return LLMProviderError(f"Ollama connection error: {str(e)}")
        return LLMProviderError(f"Unexpected Ollama provider error: {str(e)}")

    def _execute_complete(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> LLMResponse:
        client = self._get_client()
        options = self._build_options(temperature, max_tokens)
        kwargs = {
            "model": self.model_name,
            "prompt": user_prompt,
            "options": options,
            "stream": False,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if json_mode:
            kwargs["format"] = "json"

        try:
            response = client.generate(**kwargs)
            
            input_tokens = response.get("prompt_eval_count", 0)
            output_tokens = response.get("eval_count", 0)
            
            return LLMResponse(
                text=response.get("response", ""),
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
        options = self._build_options(temperature, max_tokens)
        kwargs = {
            "model": self.model_name,
            "prompt": user_prompt,
            "options": options,
            "stream": True,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response_stream = client.generate(**kwargs)
            for chunk in response_stream:
                if "response" in chunk:
                    yield chunk["response"]
        except Exception as e:
            raise self._handle_api_error(e) from e

    async def _execute_acomplete(
        self, system_prompt: str | None, user_prompt: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> LLMResponse:
        client = self._get_async_client()
        options = self._build_options(temperature, max_tokens)
        kwargs = {
            "model": self.model_name,
            "prompt": user_prompt,
            "options": options,
            "stream": False,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if json_mode:
            kwargs["format"] = "json"

        try:
            response = await client.generate(**kwargs)
            
            input_tokens = response.get("prompt_eval_count", 0)
            output_tokens = response.get("eval_count", 0)
            
            return LLMResponse(
                text=response.get("response", ""),
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
        client = self._get_async_client()
        options = self._build_options(temperature, max_tokens)
        kwargs = {
            "model": self.model_name,
            "prompt": user_prompt,
            "options": options,
            "stream": True,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response_stream = await client.generate(**kwargs)
            async for chunk in response_stream:
                if "response" in chunk:
                    yield chunk["response"]
        except Exception as e:
            raise self._handle_api_error(e) from e
