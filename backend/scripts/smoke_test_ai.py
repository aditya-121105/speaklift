import os
import sys
import time

# Ensure backend/ is in sys.path if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.ai.llm.factory import get_llm_service
from app.ai.llm.prompts.base import Prompt, PromptVersion


def run_smoke_test():
    print("=" * 50)
    print("             AI PIPELINE SMOKE TEST")
    print("=" * 50)

    start_time = time.time()

    try:
        service = get_llm_service()

        prompt = Prompt(
            name="smoke_test",
            version=PromptVersion(major=1, minor=0),
            system_prompt="You are a helpful AI assistant. Keep responses brief.",
            user_prompt="Say 'Hello, SpeakLift!' and nothing else.",
        )

        response = service.generate_response(
            prompt,
            max_tokens=256,
            temperature=0.0,
        )

        duration = time.time() - start_time
        
        if not response.text or not response.text.strip():
            raise ValueError("Provider returned an empty response text.")

        input_tokens = response.input_tokens or 0
        output_tokens = response.output_tokens or 0
        total_tokens = input_tokens + output_tokens

        print(f"Status            : [ PASS ]")
        print(f"Active Provider   : {response.provider}")
        print(f"Active Model      : {response.model}")
        print(f"Routing Strategy  : {settings.LLM_ROUTING_STRATEGY}")
        print()

        print("--------------- Prompt ---------------")
        print(prompt.user_prompt)
        print("--------------------------------------")
        print()

        print("-------------- Response --------------")
        print(repr(response.text))
        print("--------------------------------------")
        print()

        print("--------------- Tokens ---------------")
        print(f"Prompt Tokens     : {input_tokens}")
        print(f"Completion Tokens : {output_tokens}")
        print(f"Total Tokens      : {total_tokens}")
        print("--------------------------------------")
        print()

        print("------------- Raw Metadata -----------")

        # These getattr() calls make the smoke test resilient
        # if LLMResponse changes in the future.
        print(f"Provider          : {getattr(response, 'provider', None)}")
        print(f"Model             : {getattr(response, 'model', None)}")
        print(f"Input Tokens      : {getattr(response, 'input_tokens', None)}")
        print(f"Output Tokens     : {getattr(response, 'output_tokens', None)}")
        print(f"Metadata          : {getattr(response, 'metadata', None)}")

        print("--------------------------------------")
        print(f"Response Time     : {duration:.2f} seconds")
        print("=" * 50)

    except Exception as e:
        duration = time.time() - start_time

        print(f"Status            : [ FAIL ]")
        print(f"Exception Type    : {type(e).__name__}")
        print(f"Error             : {e}")
        print(f"Elapsed Time      : {duration:.2f} seconds")
        print("=" * 50)
        raise


if __name__ == "__main__":
    run_smoke_test()