"""
Simple text message program.
Goal: Send text message at a scheduled time or frequency.

Have a set of random messages you want to send.
Send message with some sort of text message API. (We are using Twilio.)
Schedule the messages.
"""


# TODO: for continuing project:
#
# Add a user_info class to have all the information in one object to be able to use in our functions and lessen the amount of parameters needed.
# Repeating parameters in multiple function calls probably means we need to create an object and have attributes/methods there.


import random
import json
import time
import schedule
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class TwilioAccount:
    """A class to encapsulate data about Twilio information, like associated numbers and tokens and such."""

    def __init__(self, file_name):
        self.file_name = file_name
        # Instantiate attributes from our import json method below.
        if self.import_json_credentials():  # If file exists.
            (
                self.account,
                self.token,
                self.sender_cell_number,
                self.receiver_cell_number,
            ) = self.import_json_credentials()

    def import_json_credentials(self):
        """import credentials from json file."""
        # Make sure dictionary variables include account and token.
        try:
            with open(self.file_name) as file_object:
                file_content = json.load(file_object)
                # Included None default method in case these attributes are being assigned.
                account = file_content.get("account", None)
                token = file_content.get("token", None)
                sender_cell_number = file_content.get("sender_cell_number", None)
                receiver_cell_number = file_content.get("receiver_cell_number", None)
            return account, token, sender_cell_number, receiver_cell_number
        except FileNotFoundError:
            return False


def send_message(account_info, message):
    """Send message using twilio API. Need twilio credentials (need to register for free)."""
    if (
        not account_info.account
        or not account_info.token
        or not account_info.sender_cell_number
        or not account_info.receiver_cell_number
        or not message
    ):
        print("Sorry, one of your credentials is missing. Please try again.")
        return None
    try:
        client = Client(account_info.account, account_info.token)
        client.messages.create(
            to=account_info.receiver_cell_number,
            from_=account_info.sender_cell_number,
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


def schedule_message(account_info, message):
    """Schedules a message based on your criteria. Requirements are Account Id and Token
    given by Twilio, sender cell phone number and receiver cell phone number linked with twilio, and a custom message."""
    while True:
        user_input = input(
            "Press 1 if you want to repeat a schedule every X minutes. Press 2 if you want to repeat a schedule daily at a certain time: "
        )

        if user_input == "1":
            # Schedule minutes or hours.
            schedule_timely(account_info, message)
            return

        elif user_input == "2":
            # Schedule daily at certain time.
            schedule_daily(account_info, message)
            return
        else:
            print("Sorry, those were not one of the choices. Please try again.")
            continue


def schedule_daily(
    account_info,
    message,
    hour=None,
    minute=None,
):
    """Schedules text message every day at a chosen time."""
    if hour is None:
        while True:
            try:
                hour = input(
                    "Enter what hour you want to send the message at (remember 24 hour time): "
                )
                if int(hour) < 0 or int(hour) > 23:
                    print("That hour is not in the 24 hour range. Try again.")
                    continue
                minute = input("Enter what minutes you want to send the message at: ")
                if int(minute) < 0 or int(minute) > 59:
                    print("That hour is not in the 60 minute range. Try again.")
                    continue
            except ValueError:
                print("Please enter valid numbers. Try again.")
                continue
            else:
                # Enter schedule function.
                # The time in .at() is passed as a string in the format hr:min.
                schedule.every().day.at(f"{hour}:{minute}").do(
                    send_message,
                    account_info,
                    message,
                )
                return
    else:
        if minute is None:
            minute = "0"
        schedule.every().day.at(f"{hour}:{minute}").do(
            send_message,
            account_info,
            message,
        )
    return


def schedule_timely(account_info, message):
    """Schedules text message every minute or every hour."""
    while True:
        time_metric = input(
            "Enter m to schedule every minute. Enter h to schedule every hour: "
        ).lower()
        if time_metric == "m":
            while True:
                try:
                    num_of_mins = int(input("How many minutes would you like to put: "))
                except ValueError:
                    print("Sorry, that is not a number. Please enter a number.")
                    continue

                else:
                    schedule.every(num_of_mins).minutes.do(
                        send_message,
                        account_info,
                        message,
                    )
                    return

        elif time_metric == "h":
            while True:
                try:
                    num_of_hours = int(input("How many hours would you like to put: "))
                except ValueError:
                    print("Sorry, that is not a number. Please try again.")
                    continue
                else:
                    schedule.every(num_of_hours).hours.do(
                        send_message,
                        account_info,
                        message,
                    )
                    return
        else:
            print("That's neither an h or an m. Please try again.")
            continue


def main():
    """Get credentials to use the send_message function."""
    # NOTE: Replace with your own credentials file.
    # file_name = "PUSH_TO_GITHUB/schedule_text/sample_credentials.json"
    # Fill your message_bank with custom messages
    file_name = "secrets.json"
    account_info = TwilioAccount(file_name)
    message_bank = [
        "Good Morning",
        "Top of the morning fam!",
        "Hope you have a wonderful day!",
    ]

    if account_info.import_json_credentials():
        user_input = input(
            "Enter 1 if you want to schedule your message or Enter 2 if you want to send your message NOW: "
        )
        if user_input == "1":
            # Choose Schedule Function.
            schedule_message(
                account_info,
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
                account_info,
                random.choice(message_bank),
            )
    else:
        # Does not execute any of our scheduling/ main functions.
        print("Sorry, FILE DOES NOT EXIST. Make sure your file name is correct.")


if __name__ == "__main__":
    main()
