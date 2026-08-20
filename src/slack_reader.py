import time
from http.client import IncompleteRead

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from datetime import datetime, timedelta, timezone

from config import SLACK_TOKEN

MAX_CHANNELS_PER_REQUEST = 200

client = WebClient(token=SLACK_TOKEN)

def slack_api_call_with_retry(api_call, **kwargs):
    for attempt in range(3):
        try:
            return api_call(**kwargs)
        except IncompleteRead:
            if attempt == 2:
                raise
            time.sleep(2)


def get_all_channels() -> list:
    """
    Fetch all public and private channels using pagination.
    Retries transient network errors.
    """

    all_channels = []
    cursor = None

    try:
        while True:

            for attempt in range(3):

                try:
                    response = client.conversations_list(
                        types="public_channel,private_channel",
                        exclude_archived=True,
                        limit=MAX_CHANNELS_PER_REQUEST,
                        cursor=cursor,
                    )

                    break

                except IncompleteRead:
                    if attempt == 2:
                        raise

                    time.sleep(2)

            all_channels.extend(response["channels"])

            cursor = response.get(
                "response_metadata", {}
            ).get("next_cursor")

            if not cursor:
                break

        return all_channels

    except SlackApiError as e:
        raise RuntimeError(
            f"Failed to fetch channels: {e.response['error']}"
        )


def get_channel_messages(
    channel_id: str,
    limit: int = 1000,
    days: int | None = None,
):
    """
    Fetches Slack messages with pagination.

    If 'days' is provided, only messages from the last
    'days' days are returned.
    """

    try:
        oldest = None

        if days is not None:
            oldest = (
                datetime.now(timezone.utc)
                - timedelta(days=days)
            ).timestamp()

        all_messages = []
        cursor = None

        while True:

            params = {
                "channel": channel_id,
                "limit": min(limit, 1000),
            }

            if oldest is not None:
                params["oldest"] = str(oldest)

            if cursor:
                params["cursor"] = cursor

            response = client.conversations_history(**params)

            all_messages.extend(response["messages"])

            cursor = response.get(
                "response_metadata", {}
            ).get("next_cursor")

            if not cursor:
                break

        print(
            f"Fetched {len(all_messages)} messages "
            f"from the last {days} days."
        )

        if all_messages:
            print(
                "Oldest fetched:",
                datetime.fromtimestamp(
                    float(all_messages[-1]["ts"]),
                    timezone.utc
                )
            )

            print(
                "Newest fetched:",
                datetime.fromtimestamp(
                    float(all_messages[0]["ts"]),
                    timezone.utc
                )
            )
        return all_messages

    except SlackApiError as e:
        raise RuntimeError(
            f"Failed to fetch messages for channel '{channel_id}': "
            f"{e.response['error']}"
        )

def get_channel_messages_since(
    channel_id: str,
    oldest_ts: str,
    limit: int = 1000,
):
    """
    Fetches all messages newer than the given timestamp.
    """

    try:
        all_messages = []
        cursor = None

        while True:

            params = {
                "channel": channel_id,
                "oldest": oldest_ts,
                "limit": min(limit, 1000),
            }

            if cursor:
                params["cursor"] = cursor

            response = client.conversations_history(**params)

            all_messages.extend(response["messages"])

            cursor = response.get(
                "response_metadata", {}
            ).get("next_cursor")

            if not cursor:
                break

        return all_messages

    except SlackApiError as e:
        raise RuntimeError(
            f"Failed to fetch messages since '{oldest_ts}': "
            f"{e.response['error']}"
        )


def get_user_name(user_id: str) -> str:
    """
    Returns the display name (or real name) of a Slack user.
    """
    try:
        response = client.users_info(user=user_id)

        profile = response["user"]["profile"]

        return (
            profile.get("display_name")
            or profile.get("real_name")
            or response["user"]["name"]
        )

    except SlackApiError as e:
        raise RuntimeError(
            f"Failed to fetch user '{user_id}': {e.response['error']}"
        )

def get_thread_messages(
    channel_id: str,
    thread_ts: str,
) -> list:
    """
    Fetches all replies in a Slack thread with pagination.
    """

    try:
        all_messages = []
        cursor = None

        while True:

            params = {
                "channel": channel_id,
                "ts": thread_ts,
            }

            if cursor:
                params["cursor"] = cursor

            response = client.conversations_replies(**params)

            all_messages.extend(response["messages"])

            cursor = response.get(
                "response_metadata", {}
            ).get("next_cursor")

            if not cursor:
                break

        # First message is the parent
        return all_messages[1:]

    except SlackApiError as e:
        raise RuntimeError(
            f"Failed to fetch thread '{thread_ts}': "
            f"{e.response['error']}"
        )