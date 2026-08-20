"""
Centralized configuration for the Student Check-in application.

Loads environment variables from the .env file and exposes them
as module-level constants.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# =====================================================
# Slack
# =====================================================

SLACK_TOKEN = os.getenv("SLACK_TOKEN")

# =====================================================
# Ollama
# =====================================================

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
# =====================================================
# Snowflake
# =====================================================

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")


#=====================================================
#Channel
#====================================================

TEST_CHANNELS = [
    channel.strip().lower()
    for channel in os.getenv("TEST_CHANNELS", "").split(",")
    if channel.strip()
]
