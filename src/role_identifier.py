UNKNOWN_USER = "Unknown"


def identify_student_from_channel(
    channel_name: str,
    users: list[str]
) -> str | None:
    """
    Identify the student by comparing the channel name
    with the list of users.

    Returns the best matching user, or None.
    """

    channel_tokens = channel_name.lower().replace("_", "-").split("-")

    best_match = None
    best_score = 0

    for user in users:
        user_lower = user.lower()

        score = sum(
            token in user_lower
            for token in channel_tokens
        )

        if score > best_score:
            best_score = score
            best_match = user

    return best_match


def identify_roles(
    channel_name: str,
    cleaned_messages: list
) -> dict:
    """
    Identify the student and classify all remaining users
    as participants.
    """

    users = sorted({
        msg["user"]
        for msg in cleaned_messages
        if msg.get("user") and msg["user"] != UNKNOWN_USER
    })

    student = identify_student_from_channel(channel_name, users)

    participants = [
        user
        for user in users
        if user != student
    ]

    roles = {}

    if student:
        roles[student] = "Student"

    for participant in participants:
        roles[participant] = "Participant"

    return {
        "student": student,
        "participants": participants,
        "roles": roles,
    }