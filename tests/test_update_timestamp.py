from src.snowflake_db import SnowflakeDB

db = SnowflakeDB()
db.connect()

db.update_last_processed_ts(
    channel_id="C08ABC123",
    last_processed_ts="1782150511.551330",
)

print("✅ Timestamp updated.")

db.close()