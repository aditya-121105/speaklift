import json
import re
from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError

from app.ai.llm.routers.router import LLMRouter
from app.ai.llm.providers import LLMResponse
from app.ai.llm.prompts.base import Prompt
from app.ai.shared.exceptions import AIValidationError

T = TypeVar('T', bound=BaseModel)

class LLMService:
    """
    Centralized AI orchestration service.
    
    Acts as the sole public entry point for all AI interactions,
    delegating to the LLMRouter and handling JSON parsing/validation.
    """

    def __init__(self, router: LLMRouter):
        self._router = router

    def _extract_and_parse_json(self, text: str, schema: Type[T]) -> T:
        """
        Robustly extracts JSON from raw LLM output, parsing and validating it
        against the provided Pydantic schema.
        """
        cleaned = text.strip()
        
        # 1. Attempt to extract from markdown code blocks
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()
        else:
            # 2. Fallback: isolate the first `{` or `[` and the last `}` or `]`
            start_idx = cleaned.find("{")
            start_bracket = cleaned.find("[")
            if start_idx == -1 or (start_bracket != -1 and start_bracket < start_idx):
                start_idx = start_bracket
                
            end_idx = cleaned.rfind("}")
            end_bracket = cleaned.rfind("]")
            if end_idx == -1 or (end_bracket != -1 and end_bracket > end_idx):
                end_idx = end_bracket
                
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                cleaned = cleaned[start_idx:end_idx+1]
                
        # 3. Parse the JSON payload
        try:
            parsed_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise AIValidationError(
                f"Failed to decode LLM JSON response. Error: {str(e)}\nRaw Text: {text}"
            ) from e
            
        # 4. Validate against Pydantic schema
        try:
            return schema.model_validate(parsed_data)
        except ValidationError as e:
            raise AIValidationError(
                f"LLM JSON validation failed for schema {schema.__name__}. Error: {str(e)}"
            ) from e

    # -----------------------------------------------------------------------
    # Synchronous API
    # -----------------------------------------------------------------------

    def generate_response(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        return self._router.complete(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        )

    def generate_text(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        response = self.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=False,
        )
        return response.text

    def generate_json(
        self,
        prompt: Prompt,
        schema: Type[T],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> T:
        response = self.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )
        return self._extract_and_parse_json(response.text, schema)

    # -----------------------------------------------------------------------
    # Asynchronous API
    # -----------------------------------------------------------------------

    async def agenerate_response(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        return await self._router.acomplete(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        )

    async def agenerate_text(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        response = await self.agenerate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=False,
        )
        return response.text

    async def agenerate_json(
        self,
        prompt: Prompt,
        schema: Type[T],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> T:
        response = await self.agenerate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )
        return self._extract_and_parse_json(response.text, schema)
