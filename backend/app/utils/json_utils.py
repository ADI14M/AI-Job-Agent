import json
import re
from typing import Any, Dict, Optional

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extracts JSON from text that might contain markdown formatting."""
    try:
        # First attempt: parse directly
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    try:
        # Second attempt: extract from markdown blocks
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        # Third attempt: find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
            
    except (json.JSONDecodeError, Exception):
        return None
        
    return None
