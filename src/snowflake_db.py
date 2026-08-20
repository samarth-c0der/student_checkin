import json
import snowflake.connector
from pathlib import Path

from config import (
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_USER,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_WAREHOUSE,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_SCHEMA,
    SNOWFLAKE_ROLE,
)


class SnowflakeDB:
    """
    Handles the Snowflake database connection.
    """

    def __init__(self) -> None:
        self.connection = None

    def connect(self) -> None:
        """
        Opens a connection to Snowflake.
        """

        if self.connection:
            return

        try:
            self.connection = snowflake.connector.connect(
                account=SNOWFLAKE_ACCOUNT,
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA,
                role=SNOWFLAKE_ROLE,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to connect to Snowflake: {e}")

    def initialize_database(self) -> None:
        """
        Creates all required database tables.
        """

        sql_file = (
            Path(__file__).resolve().parent.parent
            / "sql"
            / "create_tables.sql"
        )

        self.execute_sql_file(str(sql_file))

    def is_connected(self) -> bool:
        """
        Returns True if a connection to Snowflake is active.
        """
        return self.connection is not None

    def get_cursor(self):
        """
        Returns a Snowflake cursor.

        Raises:
            RuntimeError: If no connection exists.
        """

        if not self.connection:
            raise RuntimeError("Not connected to Snowflake.")

        return self.connection.cursor()

    def execute(self, query: str, params: tuple = None) -> None:
        """
        Executes a SQL query that does not return rows.

        Args:
            query: SQL query to execute.
            params: Optional query parameters.
        """

        cursor = self.get_cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()

        finally:
            cursor.close()

    def fetch_one(self, query: str, params: tuple = None):
        """
        Executes a SELECT query and returns a single row.

        Args:
            query: SQL query to execute.
            params: Optional query parameters.

        Returns:
            tuple | None: The first row returned, or None if no rows exist.
        """

        cursor = self.get_cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor.fetchone()

        finally:
            cursor.close()

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """
        Executes a SELECT query and returns all matching rows.

        Args:
            query: SQL query to execute.
            params: Optional query parameters.

        Returns:
            list: All rows returned by the query.
        """

        cursor = self.get_cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor.fetchall()

        finally:
            cursor.close()

    def execute_sql_file(self, file_path: str) -> None:
        """
        Executes all SQL statements contained in a .sql file.

        Args:
            file_path: Path to the SQL file.
        """

        sql_path = Path(file_path)

        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        with open(sql_path, "r", encoding="utf-8") as file:
            sql = file.read()

        statements = [
            statement.strip()
            for statement in sql.split(";")
            if statement.strip()
        ]

        for statement in statements:
            self.execute(statement)

    def insert_student(
        self,
        student_name: str,
        slack_user_id: str,
    ) -> int:
        """
        Inserts a student if they don't already exist.

        Returns:
            student_id
        """

        # Check if the student already exists
        result = self.fetch_one(
            """
            SELECT student_id
            FROM STUDENTS
            WHERE slack_user_id = %s
            """,
            (slack_user_id,),
        )

        if result:
            return result[0]

        # Insert the new student
        self.execute(
            """
            INSERT INTO STUDENTS (
                student_name,
                slack_user_id
            )
            VALUES (%s, %s)
            """,
            (
                student_name,
                slack_user_id,
            ),
        )

        # Return the generated student_id
        result = self.fetch_one(
            """
            SELECT student_id
            FROM STUDENTS
            WHERE slack_user_id = %s
            """,
            (slack_user_id,),
        )

        return result[0]

    def insert_channel(
        self,
        channel_id: str,
        channel_name: str,
        student_id: int,
    ) -> str:
        """
        Inserts a channel if it doesn't already exist.

        Returns:
            channel_id
        """

        # Check if the channel already exists
        result = self.fetch_one(
            """
            SELECT channel_id
            FROM CHANNELS
            WHERE channel_id = %s
            """,
            (channel_id,),
        )

        if result:

            self.execute(
                """
                UPDATE CHANNELS
                SET
                    channel_name = %s,
                    student_id = %s
                WHERE channel_id = %s
                """,
                (
                    channel_name,
                    student_id,
                    channel_id,
                ),
            )

            return channel_id

        # Insert new channel
        self.execute(
            """
            INSERT INTO CHANNELS
            (
                channel_id,
                channel_name,
                student_id
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                channel_id,
                channel_name,
                student_id,
            ),
        )

        return channel_id

    def get_student_for_channel(
        self,
        channel_id: str,
    ):
        """
        Returns the student mapped to a Slack channel.
        """

        result = self.fetch_one(
            """
            SELECT
                s.student_id,
                s.student_name,
                s.slack_user_id
            FROM CHANNELS c
            JOIN STUDENTS s
                ON c.student_id = s.student_id
            WHERE c.channel_id = %s
            """,
            (channel_id,),
        )

        if not result:
            return None

        return {
            "student_id": result[0],
            "student_name": result[1],
            "slack_user_id": result[2],
        }

    def update_last_processed_ts(
        self,
        channel_id: str,
        last_processed_ts: str,
    ) -> None:
        """
        Updates the latest processed Slack timestamp for a channel.

        Args:
            channel_id: Slack channel ID.
            last_processed_ts: Timestamp of the newest processed message.
        """

        self.execute(
            """
            UPDATE CHANNELS
            SET last_processed_ts = %s
            WHERE channel_id = %s
            """,
            (
                last_processed_ts,
                channel_id,
            ),
        )

    def get_last_processed_ts(
        self,
        channel_id: str,
    ) -> str | None:
        """
        Returns the last processed Slack timestamp for a channel.

        Args:
            channel_id: Slack channel ID.

        Returns:
            Last processed timestamp or None.
        """

        result = self.fetch_one(
            """
            SELECT last_processed_ts
            FROM CHANNELS
            WHERE channel_id = %s
            """,
            (channel_id,),
        )

        if result:
            return result[0]

        return None

    def save_checkin_history(
        self,
        student_id: int,
        channel_id: str,
        prompt: str,
        raw_response: str,
        analysis: dict,
        checkin_message: str,
    ) -> None:
        """
        Saves one AI-generated weekly check-in.
        """

        self.execute(
            """
            INSERT INTO CHECKIN_HISTORY
            (
                student_id,
                channel_id,
                prompt,
                raw_response,
                analysis_json,
                checkin_message
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                student_id,
                channel_id,
                prompt,
                raw_response,
                json.dumps(analysis),
                checkin_message,
            ),
        )

    def close(self) -> None:
        """
        Closes the Snowflake connection.
        """

        if self.connection:
            self.connection.close()
            self.connection = None