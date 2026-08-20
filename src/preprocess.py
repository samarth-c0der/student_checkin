from src.slack_reader import get_user_name

import re

UNKNOWN_USER = "Unknown"

IGNORE_MESSAGES = {
    "hi",
    "hello",
    "hey",
    "ok",
    "okay",
    "thanks",
    "thank you",
    "👍",
    "👌",
}


def clean_messages(messages: list) -> list:
    """
    Cleans Slack messages by:
    - Replacing Slack user IDs with names
    - Preserving the Slack user ID
    - Removing system messages
    - Removing trivial messages
    - Removing Slack markdown
    - Keeping only fields needed by the application
    """

    cleaned = []
    user_cache = {}

    def replace_mentions(match):
        """
        Replaces Slack user mentions with display names.
        """

        mentioned_user_id = match.group(1)

        if mentioned_user_id not in user_cache:
            user_cache[mentioned_user_id] = get_user_name(
                mentioned_user_id
            )

        return user_cache.get(
            mentioned_user_id,
            UNKNOWN_USER,
        )

    for msg in messages:

        # Ignore Slack system messages
        if msg.get("subtype"):
            continue

        # -----------------------------
        # Clean message text
        # -----------------------------

        text = msg.get("text", "").strip()

        # Replace Slack mentions with display names
        text = re.sub(
            r"<@([A-Z0-9]+)>",
            replace_mentions,
            text,
        )

        # Replace Slack links with readable labels
        text = re.sub(
            r"<https?://[^|>]+\|([^>]+)>",
            r"[Link: \1]",
            text,
            flags=re.IGNORECASE,
        )

        # Replace unlabeled Slack links
        text = re.sub(
            r"<https?://[^>]+>",
            "[Link]",
            text,
            flags=re.IGNORECASE,
        )

        # Remove Slack markdown
        text = (
            text.replace("```", "")
                .replace("`", "")
                .strip()
        )

        # Collapse multiple spaces
        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        # Ignore empty 
        if not text:
            continue

        # Ignore trivial messages
        if text.lower() in IGNORE_MESSAGES:
            continue

        user_id = msg.get("user")
        user_name = UNKNOWN_USER

        if user_id:
            if user_id not in user_cache:
                user_cache[user_id] = get_user_name(user_id)

            user_name = user_cache[user_id]

        cleaned.append(
            {
                "slack_user_id": user_id,
                "user": user_name,
                "text": text,
                "timestamp": msg.get("ts"),
                "is_bot": bool(msg.get("bot_id")),
            }
        )

    return cleaned