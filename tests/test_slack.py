from src.slack_reader import get_channel_messages
from src.preprocess import clean_messages

CHANNEL_ID = "C062MTLS92A"

messages = get_channel_messages(CHANNEL_ID, limit=20)

cleaned = clean_messages(messages)

for msg in cleaned:
    print(msg)