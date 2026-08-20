from config import  TEST_CHANNELS
   

from src.preprocess import clean_messages
from src.role_identifier import identify_roles
from src.slack_reader import (
    get_all_channels,
    get_channel_messages,
    get_channel_messages_since,
    get_thread_messages,
)
from src.snowflake_db import SnowflakeDB

from src.function1 import analyze_weekly_conversation
from src.function2 import generate_weekly_checkin


import time

DEVELOPMENT_MODE = True

def run_pipeline() -> None:
    """
    Runs the Student Check-in pipeline.
    """

    pipeline_start = time.perf_counter()

    db = SnowflakeDB()

    try:
        db.connect()
        db.initialize_database()

        channels = get_all_channels()

        if not channels:
            print("No Slack channels found.")
            return

        # --------------------------------------------------
        # Filter configured test channels
        # --------------------------------------------------

        test_channels = [
            channel
            for channel in channels
            if channel["name"].lower() in TEST_CHANNELS
        ]

        if not test_channels:
            print("No configured test channels found.")
            return

        print("\nConfigured test channels:")

        for channel in test_channels:
            print(f"- {channel['name']} ({channel['id']})")

        # --------------------------------------------------
        # Process each configured test channel
        # --------------------------------------------------

        for channel in test_channels:

            channel_id = channel["id"]
            channel_name = channel["name"]

            print("\n" + "=" * 60)
            print(f"Processing channel: {channel_name}")
            print("=" * 60)

            # ----------------------------------------------
            # Read only new messages
            # ----------------------------------------------
            
            if DEVELOPMENT_MODE:
                messages = get_channel_messages(
                    channel_id,
                    days=7,
                )
            
            else:
                last_processed_ts = db.get_last_processed_ts(channel_id)

                if last_processed_ts:
                    messages = get_channel_messages_since(
                        channel_id,
                        last_processed_ts,
                    )
                else:
                    print(
                        "First time processing channel "
                        "- fetching last 7 days only."
                    )

                    messages = get_channel_messages(
                        channel_id,
                        days=7,
                    )
            

            print(f"Retrieved {len(messages)} messages.")

            all_messages = []

            for message in messages:
                all_messages.append(message)

                if message.get("reply_count", 0) > 0:
                    replies = get_thread_messages(
                        channel_id,
                        message["ts"],
                    )

                    print(
                    f"Thread for {message['ts']} -> {len(replies)} replies"
                )

                    all_messages.extend(replies)

            messages = sorted(
                all_messages,
                key=lambda message: float(message["ts"])
            )

            print(f"Total messages after merging: {len(messages)}")

            if not messages:
                print("No new messages.")
                continue

            # ----------------------------------------------
            # Clean messages
            # ----------------------------------------------

            cleaned_messages = clean_messages(messages)

            print(
                f"Retained {len(cleaned_messages)} "
                f"meaningful messages after preprocessing."
            )

            cleaned_messages = sorted(
                cleaned_messages,
                key=lambda message: float(message["timestamp"])
            )

            if not cleaned_messages:
                print("No valid user messages to process.")
                continue

            # ----------------------------------------------
            # Load student from database if available
            # ----------------------------------------------

            student = db.get_student_for_channel(channel_id)

            if student:

                # ------------------------------------------
                # Existing channel
                # ------------------------------------------

                student_id = student["student_id"]
                student_name = student["student_name"]
                student_slack_id = student["slack_user_id"]

                participants = sorted({
                    message["user"]
                    for message in cleaned_messages
                    if (
                        message["user"] != student_name
                        and message["user"] != "Unknown"
                    )
                })

                role_info = {
                    "student": student_name,
                    "participants": participants,
                }

                print(f"Student: {student_name} (loaded from database)")

            else:

                # ------------------------------------------
                # First time processing this channel
                # ------------------------------------------

                role_info = identify_roles(
                    channel_name,
                    cleaned_messages,
                )

                student_name = role_info["student"]

                # Temporary fallback for single-user test channels
                if not student_name:

                    users = {
                        message["user"]
                        for message in cleaned_messages
                        if message["user"] != "Unknown"
                    }

                    if len(users) == 1:
                        student_name = users.pop()
                        role_info["student"] = student_name

                        if student_name in role_info["participants"]:
                            role_info["participants"].remove(student_name)

                        print(
                            f"Using single-user fallback: {student_name}"
                        )

                    else:
                        print("Could not identify student.")
                        continue

                # ------------------------------------------
                # Find student's Slack ID
                # ------------------------------------------

                student_slack_id = None

                for message in cleaned_messages:

                    if message["user"] == student_name:
                        student_slack_id = message["slack_user_id"]
                        break

                if not student_slack_id:
                    print("Student Slack ID not found.")
                    continue

                # ------------------------------------------
                # Save student
                # ------------------------------------------

                student_id = db.insert_student(
                    student_name,
                    student_slack_id,
                )

                # ------------------------------------------
                # Save channel mapping
                # ------------------------------------------

                db.insert_channel(
                    channel_id,
                    channel_name,
                    student_id,
                )

            print(f"Student: {student_name}")
            print(f"Student ID: {student_id}")  

            student_message_count = sum(
                1
                for message in cleaned_messages
                if message["user"] == student_name
            )

            participant_message_count = (
                len(cleaned_messages)
                - student_message_count                
            )

            print("\nConversation Statistics")
            print("-----------------------")
            print(f"Student messages: {student_message_count}")
            print(f"Participant messages: {participant_message_count}")      
        
            # ----------------------------------------------
            # Build AI prompt
            # ----------------------------------------------
            print("\nRunning Function 1...\n")

            llm_start = time.perf_counter()

            result = analyze_weekly_conversation(
                cleaned_messages=cleaned_messages,
                role_info=role_info,
            )

            llm_elapsed = time.perf_counter() - llm_start

            print(f"Function 1 completed in {llm_elapsed:.2f} seconds.\n")

            print("========== FUNCTION 1 OUTPUT ==========\n")
            print(result)
            print("\n=======================================\n")

            if not result["generate_checkin"]:
                print("No check-in required.")

                latest_ts = str(
                    max(
                        float(message["timestamp"])
                        for message in cleaned_messages
                    )
                )

                db.update_last_processed_ts(
                    channel_id,
                    latest_ts,
                )

                print("Channel timestamp updated.")
                continue

            print("Proceeding to Function 2...")
            
            print("\nRunning Function 2...\n")

            llm_start = time.perf_counter()

            function2_result = generate_weekly_checkin(
                cleaned_messages=cleaned_messages,
                role_info=role_info,
                function1_result=result,
            )

            llm_elapsed = time.perf_counter() - llm_start

            print(f"Function 2 completed in {llm_elapsed:.2f} seconds.\n")

            parsed = function2_result["parsed_response"]

            db.save_checkin_history(
                student_id=student_id,
                channel_id=channel_id,
                prompt=function2_result["prompt"],
                raw_response=function2_result["raw_response"],
                analysis=parsed["analysis"],
                checkin_message=parsed["checkin_message"],
            )

            print("Check-in saved to Snowflake.")

            print("========== FUNCTION 2 OUTPUT ==========\n")

            print("========== ANALYSIS ==========\n")

            analysis = parsed["analysis"]

            print("Weekly Summary:")
            print(analysis["weekly_summary"])

            print("\nMajor Topics:")
            for topic in analysis["major_topics"]:
                print(f"- {topic}")

            print("\nStudent State:")

            state = analysis["student_state"]

            print(f"Sentiment : {state['sentiment']}")
            print(f"Engagement: {state['engagement']}")
            print(f"Confidence: {state['confidence']}")

            print("\nProgress:")
            for item in analysis["progress"]:
                print(f"- {item}")

            print("\nOpen Items:")
            for item in analysis["open_items"]:
                print(f"- {item}")

            print("\nMentor Commitments:")
            for item in analysis["mentor_commitments"]:
                print(f"- {item}")

            print("\nFollow-up Focus:")
            for item in analysis["follow_up_focus"]:
                print(f"- {item}")

            print("\n========== CHECK-IN ==========\n")

            print(parsed["checkin_message"])

            print("\n=======================================\n")
                        
            # ----------------------------------------------
            # Update last processed timestamp
            # ----------------------------------------------
            
            latest_ts = str(
                max(
                    float(message["timestamp"])
                    for message in cleaned_messages
                )
            )

            db.update_last_processed_ts(
                channel_id,
                latest_ts,
            )

            print("Channel timestamp updated.")

        # ----------------------------------------------
        # Pipeline completed
        # ----------------------------------------------        
        print("\n" + "=" * 60)
        print("Pipeline completed successfully.")
        print(f"Processed {len(test_channels)} configured channel(s).")
        

        pipeline_elapsed = time.perf_counter() - pipeline_start

        print(f"Completed in {pipeline_elapsed:.2f} seconds.")

        print("=" * 60)   

    finally:
        db.close()