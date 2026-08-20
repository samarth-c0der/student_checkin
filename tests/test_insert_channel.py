from src.snowflake_db import SnowflakeDB

db = SnowflakeDB()

db.connect()

channel_id = db.insert_channel(
    channel_id="C08ABC123",
    channel_name="chinna-vatsavai",
    student_id=1,
)

print(f"Channel ID: {channel_id}")

db.close()