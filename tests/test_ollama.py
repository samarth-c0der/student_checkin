import ollama

messages = [
    {
        "role": "user",
        "content": """
You are a Customer Success Manager.

Here is a student's Slack conversation.

Student:
Hey! I completed SQL joins today.

Mentor:
Awesome! Try learning Snowflake next.

Student:
Started Snowflake yesterday. Finding it interesting.

Write a friendly personalized check-in message.
"""
    }
]

response = ollama.chat(
    model="llama3",
    messages=messages
)

print(response["message"]["content"])