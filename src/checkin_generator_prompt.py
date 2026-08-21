from pathlib import Path


def load_prompt_template() -> str:
    """
    Loads the check-in generator prompt template.
    """
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "checkin_generator_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


PROMPT_TEMPLATE = load_prompt_template()


def build_checkin_generator_prompt(
    cleaned_messages: list,
    role_info: dict,
    checkin_decision_result: dict,
) -> str:
    """
    Builds the prompt for the check-in generator function.
    """

    student = role_info["student"]

    participants = sorted(
        {
            msg["user"]
            for msg in cleaned_messages
            if msg["user"] != student
            and msg["user"] != "Unknown"
        }
    )

    prompt_parts = []

    # =====================================================
    # Student Information
    # =====================================================

    prompt_parts.append("========== STUDENT INFORMATION ==========\n")

    prompt_parts.append(f"Student:\n{student}\n")

    prompt_parts.append("Other Participants:")

    if participants:
        for participant in participants:
            prompt_parts.append(f"- {participant}")
    else:
        prompt_parts.append("None")


    # =====================================================
    # Check-in Decision Result
    # =====================================================

    prompt_parts.append("\n========== CHECK-IN DECISION RESULT ==========\n")

    prompt_parts.append(
        f"Generate Check-in:\n{checkin_decision_result['generate_checkin']}\n"
    )

    prompt_parts.append(
        f"Student Sentiment:\n{checkin_decision_result['student_sentiment']}"
    )

    # =====================================================
    # Conversation
    # =====================================================

    prompt_parts.append("\n========== CONVERSATION ==========\n")

    for msg in cleaned_messages:

        text = msg["text"].strip()

        if not text:
            continue

        user = msg["user"]

        if user == student:
            prompt_parts.append(f"{user} (Student):")
        else:
            prompt_parts.append(f"{user} (Participant):")

        prompt_parts.append(text)
        prompt_parts.append("")

    # =====================================================
    # Instructions
    # =====================================================

    prompt_parts.append(PROMPT_TEMPLATE)

    return "\n".join(prompt_parts)