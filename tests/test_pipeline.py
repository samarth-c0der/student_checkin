from src.prompt_builder import build_prompt
from src.ollama_client import generate_checkin

cleaned_messages = [
    {
        "user": "Monica",
        "text": "Please finish your SQL assignment."
    },
    {
        "user": "Chinna",
        "text": "I completed it yesterday."
    }
]

role_info = {
    "student": "Chinna",
    "participants": ["Monica"]
}

prompt = build_prompt(
    cleaned_messages,
    role_info,
    previous_analysis="Student was learning SQL.",
    previous_checkin="Complete the SQL assignment."
)

response = generate_checkin(prompt)

print(response)