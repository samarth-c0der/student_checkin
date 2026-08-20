from src.models import AIResult
from src.snowflake_db import SnowflakeDB

db = SnowflakeDB()
db.connect()

result = AIResult(
    prompt="This is a sample prompt.",
    raw_response="""
{
    "analysis": {
        "summary": "Completed SQL assignment.",
        "new_progress": ["Completed SQL assignment"],
        "pending_tasks": ["Learn Snowflake"],
        "blockers": [],
        "next_steps": ["Complete Story Draft"]
    },
    "check_in": "Great job completing SQL!",
    "conversation_summary": "Student completed SQL assignment."
}
""",
    parsed_response={
        "analysis": {
            "summary": "Completed SQL assignment.",
            "new_progress": ["Completed SQL assignment"],
            "pending_tasks": ["Learn Snowflake"],
            "blockers": [],
            "next_steps": ["Complete Story Draft"],
        },
        "check_in": "Great job completing SQL!",
        "conversation_summary": "Student completed SQL assignment.",
    },
)

db.save_analysis(
    student_id=1,
    channel_id="C08ABC123",
    result=result,
)

print("✅ Analysis saved successfully.")

db.close()