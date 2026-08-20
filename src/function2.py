from src.function2_prompt_builder import build_function2_prompt
from src.function2_response_parser import validate_function2_response
from src.ollama_client import call_ollama

DEBUG_FUNCTION2 = False

def generate_weekly_checkin(
    cleaned_messages: list,
    role_info: dict,
    function1_result: dict,
):
    """
    Generates the analysis and personalized weekly check-in.
    """

    prompt = build_function2_prompt(
        cleaned_messages,
        role_info,
        function1_result,
    )

    if DEBUG_FUNCTION2:
        print("\n========== FUNCTION 2 DEBUG ==========")

        print(f"\nPrompt length: {len(prompt):,} characters")

        print("\n----- FIRST 800 CHARACTERS -----")
        print(prompt[:800])

        print("\n----- FUNCTION 1 RESULT -----")
        start = prompt.find("========== FUNCTION 1 RESULT ==========")
        end = prompt.find("========== CONVERSATION ==========")
        print(prompt[start:end])

        print("\n----- FIRST 5 CONVERSATION MESSAGES -----")
        conversation_start = prompt.find("========== CONVERSATION ==========")
        print(prompt[conversation_start:conversation_start + 1500])

        print("\n----- LAST 800 CHARACTERS -----")
        print(prompt[-800:])

        print("\n========================================\n")

    raw_response = call_ollama(prompt)

    parsed_response = validate_function2_response(
        raw_response
    )

    return {
        "prompt": prompt,
        "raw_response": raw_response,
        "parsed_response": parsed_response,
    }