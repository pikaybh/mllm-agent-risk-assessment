from functools import wraps
from dotenv import load_dotenv


COMMERCIAL_MODELS = {
    "OpenAI" : [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Anthropic": [
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229"
    ]
}


load_dotenv()

def get_api_key():
    if st.runtime.using_script_run_context:
        ...