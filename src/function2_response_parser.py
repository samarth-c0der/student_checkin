import json


REQUIRED_FIELDS = {
    "analysis",
    "checkin_message",
}


REQUIRED_ANALYSIS_FIELDS = {
    "weekly_summary",
    "major_topics",
    "student_state",
    "progress",
    "open_items",
    "mentor_commitments",
    "follow_up_focus",
}


REQUIRED_STUDENT_STATE_FIELDS = {
    "sentiment",
    "engagement",
    "confidence",
}


def validate_function2_response(response_text: str) -> dict:
    """
    Validates the JSON returned by Function 2.
    """

    try:
        data = json.loads(response_text)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by Ollama: {e}")

    # --------------------------------------------------
    # Top-level fields
    # --------------------------------------------------

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Missing required field: '{field}'")

    if not isinstance(data["analysis"], dict):
        raise ValueError("'analysis' must be an object.")

    if not isinstance(data["checkin_message"], str):
        raise ValueError("'checkin_message' must be a string.")

    analysis = data["analysis"]

    # --------------------------------------------------
    # Analysis fields
    # --------------------------------------------------

    for field in REQUIRED_ANALYSIS_FIELDS:
        if field not in analysis:
            raise ValueError(
                f"Missing analysis field: '{field}'"
            )

    if not isinstance(analysis["weekly_summary"], str):
        raise ValueError(
            "'weekly_summary' must be a string."
        )

    list_fields = [
        "major_topics",
        "progress",
        "open_items",
        "mentor_commitments",
        "follow_up_focus",
    ]

    for field in list_fields:

        if not isinstance(analysis[field], list):
            raise ValueError(
                f"'{field}' must be a list."
            )

    # --------------------------------------------------
    # Student State
    # --------------------------------------------------

    student_state = analysis["student_state"]

    if not isinstance(student_state, dict):
        raise ValueError(
            "'student_state' must be an object."
        )

    for field in REQUIRED_STUDENT_STATE_FIELDS:

        if field not in student_state:
            raise ValueError(
                f"Missing student_state field: '{field}'"
            )

        if not isinstance(student_state[field], str):
            raise ValueError(
                f"'student_state.{field}' must be a string."
            )

    return data