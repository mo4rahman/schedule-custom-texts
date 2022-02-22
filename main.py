"""
Simple text message program.
Goal: Send text message at a scheduled time or frequency.

Have a set of random messages you want to send.
Send message with some sort of text message API. (We are using Twilio.)
Schedule the messages.
"""


# NOTE for continuing project:
#
# Refactor scheduling code into separate functions to make the code legible.


import random
import json
import time
import schedule
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def send_message(account, token, sender_cell_number, receiver_cell_number, message):
    """Send message using twilio API. Need twilio credentials (need to register for free)."""
    if (
        not account
        or not token
        or not sender_cell_number
        or not receiver_cell_number
        or not message
    ):
        print("Sorry, one of your credentials is missing. Please try again.")
        return None
    try:
        client = Client(account, token)
        client.messages.create(
            to=receiver_cell_number,
            from_=sender_cell_number,
            body=message,  # Add try blocks in case send message does not work.
        )

    except TwilioRestException:
        # If status code 400, it's the phone number error.
        # If status code 401, it's the account/token error
        error_code = client.http_client.last_response.status_code
        if error_code == 401:
            print(
                f"There seems to be something wrong with your account or token. Please try again."
            )
        elif error_code == 400:
            print(
                "There is an error with either the sender's phone number or the receiver's phone number. Please try again!"
            )
        else:
            print(
                f"There seems to be an error with your code. The error code is: {error_code}"
            )
        return None


def import_json_credentials(file_name):
    """import credentials from json file."""
    # Make sure dictionary variables include account and token
    try:
        with open(file_name) as file_object:
            file_content = json.load(file_object)
            account = file_content.get("account", None)
            token = file_content.get("token", None)
            sender_cell_number = file_content.get("sender_cell_number", None)
            receiver_cell_number = file_content.get("receiver_cell_number", None)

            return account, token, sender_cell_number, receiver_cell_number
    except FileNotFoundError:
        return None


def schedule_message(ACCOUNT, TOKEN, SENDER_CELL_NUMBER, RECEIVER_CELL_NUMBER, message):
    """Schedules a message based on your criteria. Requirements are Account Id and Token
    given by Twilio, sender cell phone number and receiver cell phone number linked with twilio, and a custom message."""
    while True:
        user_input = input(
            "Press 1 if you want to repeat a schedule every X minutes. Press 2 if you want to repeat a schedule daily at a certain time: "
        )

        if user_input == "1":
            # Schedule minutes or hours.
            time_metric = input(
                "Press m to schedule every minute, Press h to schedule every hour: "
            ).lower()
            if time_metric == "m":
                while True:
                    try:
                        num_of_mins = int(
                            input("How many minutes would you like to put: ")
                        )
                    except ValueError:
                        print("Sorry, that is not a number. Please enter a number.")
                        continue

                    else:
                        schedule.every(num_of_mins).minutes.do(
                            send_message,
                            ACCOUNT,
                            TOKEN,
                            SENDER_CELL_NUMBER,
                            RECEIVER_CELL_NUMBER,
                            message,
                        )
                        break

            elif time_metric == "h":
                while True:
                    try:
                        num_of_hours = int(
                            input("How many hours would you like to put: ")
                        )
                    except ValueError:
                        print("Sorry, that is not a number. Please try again.")
                        continue
                    else:

                        schedule.every(num_of_hours).hours.do(
                            send_message,
                            ACCOUNT,
                            TOKEN,
                            SENDER_CELL_NUMBER,
                            RECEIVER_CELL_NUMBER,
                            message,
                        )
                        break
            else:
                print("That's neither of the options. Please try again.")
                continue

            break
        elif user_input == "2":
            # Schedule daily at certain time.
            while True:
                try:
                    hour = input(
                        "Enter what hour you want to send the message at (remember 24 hour time): "
                    )
                    if int(hour) < 0 or int(hour) > 23:
                        print("That hour is not in the 24 hour range. Try again.")
                        continue
                    minute = input(
                        "Enter what minutes you want to send the message at: "
                    )
                    if int(minute) < 0 or int(minute) > 59:
                        print("That hour is not in the 60 minute range. Try again.")
                        continue
                except ValueError:
                    print("Please enter valid numbers. Try again.")
                    continue
                else:
                    # Enter schedule function.
                    schedule.every().day.at(f"{hour}:{minute}").do(
                        send_message,
                        ACCOUNT,
                        TOKEN,
                        SENDER_CELL_NUMBER,
                        RECEIVER_CELL_NUMBER,
                        message,
                    )
                    break
            break
        else:
            print("Sorry, those were not one of the choices. Please try again.")
            continue


def schedule_daily():
    pass


def schedule_timely():
    pass


def main():
    """Get credentials to use the send_message function."""
    # NOTE: Replace with your own credentials file.
    # file_name = "PUSH_TO_GITHUB/schedule_text/sample_credentials.json"
    # Fill your message_bank with custom messages
    file_name = "secrets.json"
    message_bank = ["Good Morning", "Hello Love", "ELLO LOVE"]

    if import_json_credentials(file_name):
        (
            ACCOUNT,
            TOKEN,
            SENDER_CELL_NUMBER,
            RECEIVER_CELL_NUMBER,
        ) = import_json_credentials(
            file_name
        )  # Unpacks all the variables returned from the function.

        user_input = input(
            "Enter 1 if you want to schedule your message or Enter 2 if you want to send your message NOW: "
        )
        if user_input == "1":
            # Choose Schedule Function.
            schedule_message(
                ACCOUNT,
                TOKEN,
                SENDER_CELL_NUMBER,
                RECEIVER_CELL_NUMBER,
                random.choice(message_bank),
            )
            while True:
                # Checking to see if a schedule task is pending or not.
                schedule.run_pending()
                time.sleep(10)
                print("pending")
        else:
            # Choose Function to send message now.
            send_message(
                ACCOUNT,
                TOKEN,
                SENDER_CELL_NUMBER,
                RECEIVER_CELL_NUMBER,
                random.choice(message_bank),
            )
    else:
        print("Sorry, FILE DOES NOT EXIST. Make sure your file name is correct.")


if __name__ == "__main__":
    main()
