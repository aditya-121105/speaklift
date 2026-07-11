from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from app.ai.shared.types import JSONValue


class PromptVersion(BaseModel):
    """
    Immutable version identifier for a prompt.
    """
    model_config = ConfigDict(frozen=True)

    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


class PromptRenderResult(BaseModel):
    """
    The deterministically rendered representation of a prompt,
    ready for consumption by an LLM provider.
    """
    model_config = ConfigDict(frozen=True)

    system_prompt: str | None
    user_prompt: str


class Prompt(BaseModel):
    """
    Immutable business artifact representing a complete LLM request.
    
    Providers consume Prompt objects. Providers never receive arbitrary
    strings directly. This ensures traceability and versioning of all AI
    interactions.
    """
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Stable identifier for the prompt type.")
    version: PromptVersion = Field(..., description="Semantic version of the prompt.")
    system_prompt: str | None = Field(default=None, description="The system instructions, if any.")
    user_prompt: str = Field(..., description="The fully resolved user prompt.")
    metadata: dict[str, JSONValue] = Field(
        default_factory=dict,
        description="Optional metadata such as expected format, parameters used, etc."
    )

    def render(self) -> PromptRenderResult:
        """
        Deterministically produces the provider-ready prompt representation.
        
        Returns
        -------
        PromptRenderResult
            The system and user prompts ready to be passed to an LLM provider.
        """
        return PromptRenderResult(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt
        )
