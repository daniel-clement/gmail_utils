# gmail_utils
Python scripts to work with GMAIL

## Setting up GMAIL app password:
Use the following website to set up an app password for your google account:
[https://support.google.com/mail/answer/185833?hl=en#zippy=](https://support.google.com/mail/answer/185833?hl=en#zippy=)

## delete_emails.py
This script can be used to delete emails from specific senders from your GMAIL account. 

### Parameters
`my_email`: This is the email for the account you want to delete emails from

`app_password`: This is the app password generated by following the instructions in the "Setting up GMAIL app password" step above.

`senders_emails_to_delete`: This is a list of the senders email addresses that you want to delete emails for. These email addresses need to be formatted inside of two quotation marks and separated by commas, and all of this needs to be inside of square brackets: []

Example: 
```
senders_emails_to_delete = ["example1@example.com", "example2@example2.com", "example3@example3.com"]
```
