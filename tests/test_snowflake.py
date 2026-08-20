from src.snowflake_db import SnowflakeDB


def main():
    db = SnowflakeDB()

    try:
        db.connect()
    finally:
        db.close()


if __name__ == "__main__":
    main()