from openai import OpenAI
from emergentintegrations.llm.openai import OpenAITextToSpeech
from pathlib import Path
from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Set FAL_KEY for fal_client
os.environ["FAL_KEY"] = os.environ.get('FAL_KEY', '')

# fal.ai OpenRouter client for LLM
llm_client = OpenAI(
    base_url="https://fal.run/openrouter/router/openai/v1",
    api_key="not-needed",
    default_headers={
        "Authorization": f"Key {os.environ.get('FAL_KEY', '')}",
    },
)

# OpenAI TTS client using Emergent LLM Key
tts_client = OpenAITextToSpeech(api_key=os.environ.get('EMERGENT_LLM_KEY', ''))
