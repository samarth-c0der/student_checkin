from src.snowflake_db import SnowflakeDB

db = SnowflakeDB()
db.connect()

messages = [
    {
        "slack_user_id": "U08BZE6RN10",
        "user": "Chinna Subbaraju Vatsavai",
        "text": "Completed SQL assignment.",
        "timestamp": "1782150511.551329",
        "is_bot": False,
    },
    {
        "slack_user_id": "U08BZE6RN10",
        "user": "Chinna Subbaraju Vatsavai",
        "text": "Started preparing for Snowflake.",
        "timestamp": "1782150511.551330",
        "is_bot": False,
    },
]

db.save_messages(
    channel_id="C08ABC123",
    messages=messages,
)

print("✅ Messages saved successfully.")

db.close()