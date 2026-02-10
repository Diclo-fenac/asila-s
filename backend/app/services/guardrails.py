from __future__ import annotations


def post_process_response(response: str) -> tuple[str, bool]:
    """
    Check response for forbidden keywords.
    Returns (response, is_safe).
    """
    forbidden = {
        "you have",
        "diagnosed with",
        "treatment for",
        "i am from",
        "official statement",
        "might be",
        "probably",
        "i think",
    }
    
    response_lower = response.lower()
    for keyword in forbidden:
        if keyword in response_lower:
            return ("I can only provide verified information. Please contact the department directly.", False)
    
    return (response, True)
