
import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL

_configured = False


def _ensure_configured():
    global _configured
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )
    if not _configured:
        genai.configure(api_key=GEMINI_API_KEY)
        _configured = True


def generate(prompt: str, system_instruction: str = None, temperature: float = 0.4) -> str:
    _ensure_configured()
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_instruction,
    )
    response = model.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": 1024},
    )
    return response.text.strip()


def is_configured() -> bool:
    return bool(GEMINI_API_KEY)
