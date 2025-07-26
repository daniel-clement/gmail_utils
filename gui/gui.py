"""
Author: Daniel Clement
Publication_date: June 2023

This script sets up the GUI framework for the `delete emails gui` script.
"""
import os.path
import sys

import PySimpleGUI as sg
from processes import main
import logging
import queue
import traceback
import webbrowser

# set up the logger
logger = logging.getLogger('Gmail Utils')


class QueueHandler(logging.Handler):
    """
    Handles the logging queue
    """

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


# set the theme
sg.theme('Dark2')
sg.theme_input_text_color('white')
sg.theme_input_background_color('grey20')
sg.theme_element_text_color("white")

# create the inputs column
inputs_column = [
    [sg.Text(text='Please input the information below, and then click the "Start" button to begin the process.')],
    [sg.Text(text='Need help creating a Gmail App Password? Click the Help button in the bottom right corner!')],

    [sg.Text('')],
    [sg.Text(text='Enter your Gmail Email Address:', tooltip="Ex. jane.doe@gmail.com"),
     sg.InputText(tooltip="Ex. jane.doe@gmail.com", enable_events=True, key="user_email")],

    [sg.Text('')],
    [sg.Text(text='Enter your Gmail App Password:', tooltip="Ex. aljkhwfioicnlnkw"),
     sg.InputText(tooltip="Ex. aljkhwfioicnlnkw", enable_events=True, key="app_pw")],

    [sg.Button(button_text='Save Credentials', button_color=("white", "palegreen4"),
               tooltip="Save your User Email and App Password to a credentials file.", enable_events=True),
     sg.Button(button_text='Load Credentials', button_color=("white", "palegreen4"),
               tooltip="Load your User Email and App Password from the previously saved credentials file.",
               enable_events=True)
     ],

    [sg.Text('')],
    [sg.Text(text='Enter the emails of the senders which you want to delete. '
                  '\nPlease enter each email address on a new line:')],

    [sg.Multiline(size=(60, 20), enable_events=True, sbar_background_color="grey42", expand_x=True, key="sender_list")],
    [sg.Button('Start', button_color="grey42", disabled_button_color="grey42", disabled=True, enable_events=True),
     sg.Button('Quit', button_color="firebrick4")]
]

# create the output column
outputs_columns = [

    [sg.Text('Progress Updates:')],
    [sg.Output(size=(70, 20),
               font="Consolas 10",
               sbar_background_color="grey42",
               echo_stdout_stderr=True,
               expand_x=True,
               expand_y=True,
               key='log'
               )
     ],

    [sg.Text('', key='-OUT-', enable_events=True, justification='center', expand_x=True)],

    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("")],

    [sg.Text("Created by Daniel Clement", font=("", 8)),
     sg.Push(),
     sg.Button(button_text="Help?",
               button_color="royalblue3",
               tooltip="Open the documentation for this tool.",
               enable_events=True,
               key="-LINK-")
     ]

]

# set up the gui windows layout
layout = [
    [
        sg.Column(inputs_column),
        sg.VSeperator(),
        sg.Column(outputs_columns)
    ]
]

# Setup logging and start app
logging.basicConfig(level=logging.DEBUG,
                    format="%(message)s"
                    )
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)

# Create the Window
icon = r"gmail_utils_icon.ico"
window = sg.Window('Gmail Clean-Up Utility', layout, resizable=True, icon=icon)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    # get the working dir and make the output txt file to store the credentials
    working_dir = os.path.dirname(sys.executable)
    txt_file_path = os.path.join(working_dir, "burn_after_reading.txt")

    if event == "Save Credentials":
        # write the credentials out to the text file
        with open(txt_file_path, "w") as txt_file:
            txt_file.write(values['user_email'] + "\n")
            txt_file.write(values['app_pw'])
        logging.info(f"\nCredentials saved to: {txt_file_path}")

    if event == "Load Credentials":
        if os.path.isfile(txt_file_path):
            with open(txt_file_path) as creds:
                email = creds.readline().split('\n', 1)[0]
                pw = creds.readline()
            # update the values of the text inputs to contain the user email and password
            window['user_email'].update(value=email)
            window['app_pw'].update(value=pw)

            logging.info(f"\nCredentials loaded successfully!")
        else:
            logging.error("\nNo credential file found. Credentials must be saved before they can be loaded.")

    # disable the start button until the input fields have received user input
    if event in ('user_email', 'app_pw', 'sender_list'):
        disabled = not (values['user_email'] and values['app_pw'] and values['sender_list'])
        window['Start'].update(disabled=disabled, button_color="palegreen4")

    elif event == "-LINK-":
        webbrowser.open("https://daniel-clement.github.io/gmail_utils/")

    # kill the process if user closes window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Quit':
        break

    # what to do when the start button is pressed
    elif event == "Start":

        # clear the output everytime start is pressed
        window['log'].Update('')

        # Poll queue
        try:
            record = log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = queue_handler.format(record)
            window['-LOG-'].update(msg + '\n', append=True)

        logging.info("\nStarting Process...")

        # turn the list of emails given by the user input into a list
        sender_list = values['sender_list'].strip().splitlines()

        # get the number of sender emails in the sender list
        number_of_senders = len(sender_list)

        # window['-PBAR-'].update(current_count=0, max=number_of_senders)

        count = 0

        # loop through the emails in sender list
        for email in sender_list:
            logging.info("")

            for i in range(number_of_senders):
                count += 1

                # update the progress bar
                # window['-PBAR-'].update(current_count=(i + 1), max=number_of_senders)
                pct_complete = int(round((((i + 1) / number_of_senders) * 100), 0))
                logging.info(f"Progress: {i + 1}/{number_of_senders} - {pct_complete}%")

                window['-OUT-'].update(f"Progress: {i + 1}/{number_of_senders} - {pct_complete}%")

            # run the main processes.py function
            if __name__ == "__main__":
                try:
                    # if user email doesnt contain `@gmail.com` print error msg
                    if "@gmail.com" not in values['user_email']:
                        raise Exception("ERROR: User email not Gmail. Tool only works with Gmail email accounts.")
                    # if app password isnt 16 characters long print error msg
                    if len(values['app_pw']) != 16:
                        raise Exception(
                            "ERROR: App password length is incorrect. App password length should be 16 characters.")
                    # if there isnt at least 1 email address in the senders list print error msg
                    if len(sender_list) < 1:
                        raise Exception("ERROR: No sender emails given. At least 1 sender email required.")

                    main(
                        email_address=email,
                        base_user_email=values['user_email'],
                        base_app_password=values['app_pw']
                    )

                except Exception as e:
                    tb = traceback.format_exc()
                    if "Invalid credentials" in tb:

                        logging.error(f"Authentication Error: App Password and/or User email were not accepted. "
                                      f"Please double check for accuracy and try again.")
                    else:
                        logging.error(f"{tb}")

window.close()
