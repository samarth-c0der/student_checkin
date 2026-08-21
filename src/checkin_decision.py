from src.checkin_decision_prompt import build_checkin_decision_prompt
from src.checkin_decision_parser import validate_checkin_decision_response
from src.ollama_client import call_ollama


def decide_checkin(
    cleaned_messages: list,
    role_info: dict,
):
    prompt = build_checkin_decision_prompt(
        cleaned_messages,
        role_info,
    )

    raw_response = call_ollama(prompt)

    parsed_response = validate_checkin_decision_response(
        raw_response
    )

    return parsed_response