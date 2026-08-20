from src.snowflake_db import SnowflakeDB


db = SnowflakeDB()

db.connect()

db.execute_sql_file("sql/create_tables.sql")

print("✅ Tables created successfully.")

db.close()