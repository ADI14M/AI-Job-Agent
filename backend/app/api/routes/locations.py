from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from rapidfuzz import fuzz

router = APIRouter()

# Global memory cache for locations
_LOCATIONS = []

class LocationResponse(BaseModel):
    id: str
    city: str
    country: Optional[str] = ""
    display: str

def load_locations():
    global _LOCATIONS
    if not _LOCATIONS:
        file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "locations.json")
        try:
            with open(file_path, "r") as f:
                _LOCATIONS = json.load(f)
        except Exception as e:
            print(f"Failed to load locations dataset: {e}")
            _LOCATIONS = []

# Load on module import
load_locations()

@router.get("/search", response_model=List[LocationResponse])
def search_locations(q: str = Query(..., min_length=1)):
    """
    Returns up to 10 location suggestions using fuzzy matching.
    Response time target: <30ms
    """
    q_lower = q.lower().strip()
    results = []
    
    for loc in _LOCATIONS:
        # Check exact matches first
        city_lower = loc["city"].lower()
        if city_lower == q_lower:
            results.append((1000, loc))
            continue
            
        # Check alias exact matches
        matched_alias_exact = False
        for alias in loc.get("aliases", []):
            if alias.lower() == q_lower:
                results.append((1000, loc))
                matched_alias_exact = True
                break
        
        if matched_alias_exact:
            continue
            
        # Check prefix/starts with
        if city_lower.startswith(q_lower):
            results.append((900, loc))
            continue
            
        matched_alias_prefix = False
        for alias in loc.get("aliases", []):
            if alias.lower().startswith(q_lower):
                results.append((900, loc))
                matched_alias_prefix = True
                break
                
        if matched_alias_prefix:
            continue
            
        # Fallback to fuzzy match on the display name
        score = fuzz.partial_ratio(q_lower, loc["display"].lower())
        if score > 75:  # Arbitrary threshold to keep decent matches
            results.append((score, loc))

    # Sort descending by score, then ascending by city length (prefer shorter city names for ties)
    results.sort(key=lambda x: (-x[0], len(x[1]["city"])))
    
    # Return top 10
    top_10 = [res[1] for res in results[:10]]
    
    return [LocationResponse(**loc) for loc in top_10]
