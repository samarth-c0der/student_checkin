from src.checkin_generator_prompt import build_checkin_generator_prompt
from src.checkin_generator_parser import validate_checkin_generator_response
from src.ollama_client import call_ollama

DEBUG_CHECKIN_GENERATOR = False

def generate_checkin(
    cleaned_messages: list,
    role_info: dict,
    checkin_decision_result: dict,
):
    """
    Generates the analysis and personalized weekly check-in.
    """

    prompt = build_checkin_generator_prompt(
        cleaned_messages,
        role_info,
        checkin_decision_result,
    )

    if DEBUG_CHECKIN_GENERATOR:
        print("\n========== CHECK-IN GENERATOR DEBUG ==========")

        print(f"\nPrompt length: {len(prompt):,} characters")

        print("\n----- FIRST 800 CHARACTERS -----")
        print(prompt[:800])

        print("\n----- CHECK-IN DECISION RESULT -----")
        start = prompt.find("========== CHECK-IN DECISION RESULT ==========")
        end = prompt.find("========== CONVERSATION ==========")
        print(prompt[start:end])

        print("\n----- FIRST 5 CONVERSATION MESSAGES -----")
        conversation_start = prompt.find("========== CONVERSATION ==========")
        print(prompt[conversation_start:conversation_start + 1500])

        print("\n----- LAST 800 CHARACTERS -----")
        print(prompt[-800:])

        print("\n========================================\n")

    raw_response = call_ollama(prompt)

    parsed_response = validate_checkin_generator_response(
        raw_response
    )

    return {
        "prompt": prompt,
        "raw_response": raw_response,
        "parsed_response": parsed_response,
    }