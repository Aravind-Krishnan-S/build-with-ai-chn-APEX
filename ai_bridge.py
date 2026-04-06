import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class MissingAPIKeyError(Exception):
    """Raised when the GEMINI_API_KEY environment variable is not set."""


def _get_api_key() -> str:
    """Return the Gemini API key or raise if missing."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise MissingAPIKeyError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file or export it as an environment variable."
        )
    return key


def _strip_code_fences(text: str) -> str:
    """Remove markdown code-block wrappers (```markdown ... ```) if present."""
    stripped = re.sub(
        r"^```(?:markdown|md)?\s*\n(.*?)```\s*$",
        r"\1",
        text.strip(),
        flags=re.DOTALL,
    )
    return stripped.strip()


SYSTEM_PROMPT = (
    "You are an expert AI developer tracking project state. "
    "Your job is to rewrite a project context document so it accurately "
    "reflects the latest code changes. Keep the exact same heading structure. "
    "Focus on updating 'Current Progress' and 'The Next Move'. "
    "Return ONLY the raw markdown content — no surrounding code fences."
)


def update_context_via_ai(current_context: str, git_diff: str) -> str:
    """Send the current context and recent changes to Gemini and return
    an updated VIBE_CONTEXT.md body.

    Args:
        current_context: The current contents of VIBE_CONTEXT.md.
        git_diff: A combined string of recent git diffs / commit info.

    Returns:
        The rewritten markdown text for VIBE_CONTEXT.md.

    Raises:
        MissingAPIKeyError: If GEMINI_API_KEY is not configured.
    """
    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = (
        f"Here is the current VIBE_CONTEXT.md:\n\n"
        f"{current_context}\n\n"
        f"---\n\n"
        f"Here are the latest code changes:\n\n"
        f"{git_diff}\n\n"
        f"---\n\n"
        f"Rewrite the VIBE_CONTEXT.md to accurately reflect the new progress, "
        f"keeping the exact same heading structure. "
        f"Focus on updating 'Current Progress' and 'The Next Move'."
    )

    response = model.generate_content(user_prompt)
    return _strip_code_fences(response.text)
