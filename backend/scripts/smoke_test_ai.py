import os
import sys
import time

# Ensure backend/ is in sys.path if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.ai.llm.factory import get_llm_service

def run_smoke_test():
    print("==================================================")
    print("             AI PIPELINE SMOKE TEST               ")
    print("==================================================")
    
    start_time = time.time()
    
    try:
        service = get_llm_service()
        
        prompt = Prompt(
            name="smoke_test",
            version=PromptVersion(major=1, minor=0),
            system_prompt="You are a helpful AI assistant. Keep responses brief.",
            user_prompt="Say 'Hello, SpeakLift!' and nothing else."
        )
        
        response = service.generate_response(prompt, max_tokens=20, temperature=0.0)
        
        duration = time.time() - start_time
        
        print(f"Status            : [ PASS ]")
        print(f"Active Provider   : {response.provider}")
        print(f"Active Model      : {response.model}")
        print(f"Routing Strategy  : {settings.LLM_ROUTING_STRATEGY}")
        print(f"Prompt            : {prompt.user_prompt}")
        print(f"Response          : {response.text.strip()}")
        print(f"Prompt Tokens     : {response.input_tokens}")
        print(f"Completion Tokens : {response.output_tokens}")
        print(f"Total Tokens      : {response.input_tokens + response.output_tokens}")
        print(f"Response Time     : {duration:.2f} seconds")
        print("==================================================")
        
    except Exception as e:
        print(f"Status            : [ FAIL ]")
        print(f"Error             : {str(e)}")
        print("==================================================")
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_test()
