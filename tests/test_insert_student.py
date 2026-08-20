from src.snowflake_db import SnowflakeDB

db = SnowflakeDB()

db.connect()

student_id = db.insert_student(
    student_name="Chinna Subbaraju Vatsavai",
    slack_user_id="U08BZE6RN10",
)

print(f"Student ID: {student_id}")

db.close()