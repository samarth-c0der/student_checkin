import json


REQUIRED_FIELDS = {
    "generate_checkin",
    "reason",
    "student_sentiment"
}

def validate_function1_response(response_text: str) -> dict:
    """
    Validates the JSON returned by Function 1.

    Args:
        response_text: Raw JSON string returned by Ollama.

    Returns:
        Parsed Python dictionary.

    Raises:
        ValueError: If the response does not match the expected schema.
    """

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by Ollama: {e}")

    # --------------------------------------------------
    # Required top-level fields
    # --------------------------------------------------

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Missing required field: '{field}'")

    # --------------------------------------------------
    # If no check-in required
    # --------------------------------------------------

    if not isinstance(data["generate_checkin"], bool):
        raise ValueError(
            "'generate_checkin' must be a boolean."
        )

    if not isinstance(data["reason"], str):
        raise ValueError("'reason' must be a string.")

    if not isinstance(data["student_sentiment"], str):
        raise ValueError("'student_sentiment' must be a string.")

    return data