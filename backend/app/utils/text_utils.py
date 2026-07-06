import re

def clean_text(text: str) -> str:
    """Removes excessive whitespace and standardizes newlines."""
    if not text:
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def truncate_text(text: str, max_length: int = 2000) -> str:
    """Truncates text to a maximum length."""
    if not text:
        return ""
    return text[:max_length] + "..." if len(text) > max_length else text
