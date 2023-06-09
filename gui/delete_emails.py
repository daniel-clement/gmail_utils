"""
@author: Daniel Clement
@publication_date: May 2023
"""

# imports
import imaplib
import logging
# import sys

from tqdm import tqdm

#
# logging.basicConfig(level=logging.INFO,
#                     stream=sys.stdout,
#                     )


# parameters
# ####################################################################################################################
# my_email = "your_email@gmail.com"
# app_password = "your app password here"
#
# senders_emails_to_delete = ["example1@example.com", "example2@example2.com", "example3@example3.com"]
# ####################################################################################################################


def delete_emails_matching_sender(
        sender_email: str,
        user_email: str,
        user_app_pw: str
) -> None:
    """
    This function will search for all the emails from the sender email,
    move them to the trash, and then empty the trash.
    :param sender_email: The email address to delete emails of
    :param user_email: your gmail email address
    :param user_app_pw: your gmail app password
    :return: Nothing
    """

    # initialize IMAP object for gmail
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    # login to gmail with credentials
    imap.login(user=user_email,
               password=user_app_pw)

    # select the Inbox
    imap.select("INBOX")

    # define your search criteria
    status, [messages] = imap.search(None, f'FROM "{sender_email}"')

    # get the number of emails found in search
    num_messages = len(messages)

    # check to see if there are any emails that meet the search criteria
    if num_messages == 0:
        logging.info(f"Not enough emails found to process email: {sender_email}")
        pass  # if there are no emails, skip that email address

    else:
        logging.info(f"\n{num_messages} found in search for: {sender_email}")
        logging.info(f"Moving emails to trash...")

        # if it's a bytes type, decode to str
        if isinstance(messages, bytes):
            msg_ids = messages.decode()

        # add a comma to separate msg entries
        msg_ids_comma = ','.join(msg_ids.split(' '))

        # use imap.store to move messages to trash
        imap.store(msg_ids_comma, '+X-GM-LABELS', '\\Trash')

        # permanently delete all messages from trash folder
        logging.info("Emptying Trash...")
        trash_folder = '[Gmail]/Trash'
        imap.select(trash_folder)
        imap.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
        imap.expunge()

    # close and then logout from the mailbox server
    imap.close()
    imap.logout()


def main(email_address: str, base_user_email: str, base_app_password: str) -> None:
    """
    Main process. loops through the list of sender emails you want to delete and delete each of them.
    :param email_address: the list of user email addresses (user defined input)
    :param base_user_email: the users email address (user defined input)
    :param base_app_password: the app password (user defined input)
    :return: None
    """

    # loop through the list of sender emails
    # for email in tqdm(email_addresses, desc="Deleting Sender Emails"):

    # run the function to delete the emails from the sender
    delete_emails_matching_sender(
        sender_email=email_address,
        user_email=base_user_email,
        user_app_pw=base_app_password
    )
