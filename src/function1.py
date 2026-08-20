from src.function1_prompt_builder import build_function1_prompt
from src.function1_response_parser import validate_function1_response
from src.ollama_client import call_ollama


def analyze_weekly_conversation(
    cleaned_messages: list,
    role_info: dict,
):
    prompt = build_function1_prompt(
        cleaned_messages,
        role_info,
    )

    raw_response = call_ollama(prompt)

    parsed_response = validate_function1_response(
        raw_response
    )

    return parsed_response