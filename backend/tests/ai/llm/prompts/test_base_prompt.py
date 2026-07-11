import pytest
from pydantic import ValidationError
from app.ai.llm.prompts.base import Prompt, PromptVersion, PromptRenderResult

def test_prompt_version():
    version = PromptVersion(major=1, minor=0)
    assert str(version) == "1.0"
    
    with pytest.raises(ValidationError):
        version.major = 2

def test_prompt_immutability():
    version = PromptVersion(major=1, minor=0)
    prompt = Prompt(
        name="test_prompt",
        version=version,
        system_prompt="You are a helpful assistant.",
        user_prompt="Hello!",
        metadata={"key": "value"}
    )
    
    with pytest.raises(ValidationError):
        prompt.user_prompt = "Goodbye!"
        
    with pytest.raises(ValidationError):
        prompt.metadata = {"new": "meta"}

def test_prompt_rendering():
    version = PromptVersion(major=2, minor=1)
    prompt = Prompt(
        name="feedback_prompt",
        version=version,
        system_prompt="System context.",
        user_prompt="Evaluate this.",
        metadata={"tone": "professional"}
    )
    
    result = prompt.render()
    assert isinstance(result, PromptRenderResult)
    assert result.system_prompt == "System context."
    assert result.user_prompt == "Evaluate this."

def test_prompt_rendering_without_system_prompt():
    version = PromptVersion(major=1, minor=0)
    prompt = Prompt(
        name="simple_prompt",
        version=version,
        user_prompt="Just asking a question."
    )
    
    result = prompt.render()
    assert result.system_prompt is None
    assert result.user_prompt == "Just asking a question."

def test_prompt_metadata():
    version = PromptVersion(major=1, minor=0)
    prompt = Prompt(
        name="metadata_prompt",
        version=version,
        user_prompt="Hi",
        metadata={"max_tokens": 100, "json_mode": True}
    )
    
    assert prompt.metadata["max_tokens"] == 100
    assert prompt.metadata["json_mode"] is True

def test_deterministic_output():
    version = PromptVersion(major=1, minor=2)
    prompt = Prompt(
        name="deterministic_test",
        version=version,
        system_prompt="Sys",
        user_prompt="User"
    )
    
    render1 = prompt.render()
    render2 = prompt.render()
    
    assert render1.system_prompt == render2.system_prompt

class MockProvider:
    pass

def test_metadata_rejects_arbitrary_objects():
    version = PromptVersion(major=1, minor=0)
    
    with pytest.raises(ValidationError):
        Prompt(
            name="bad_prompt",
            version=version,
            user_prompt="Hi",
            metadata={"provider": MockProvider()}
        )

def test_metadata_accepts_nested_primitives():
    version = PromptVersion(major=1, minor=0)
    prompt = Prompt(
        name="nested_prompt",
        version=version,
        user_prompt="Hi",
        metadata={
            "settings": {
                "temperature": 0.7,
                "retries": 3,
                "tags": ["evaluation", "v1"]
            },
            "is_active": True,
            "score": None
        }
    )
    
    assert prompt.metadata["is_active"] is True
    assert prompt.metadata["score"] is None
    assert prompt.metadata["settings"]["temperature"] == 0.7
    assert "evaluation" in prompt.metadata["settings"]["tags"]

