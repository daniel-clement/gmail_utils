import PySimpleGUI as sg
from delete_emails import main
import logging
import queue

# set up the logger
logger = logging.getLogger('mymain')


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

    [sg.Text('')],
    [sg.Text(text='Enter your Gmail Email Address:', tooltip="Ex. jane.doe@gmail.com"),
     sg.InputText(tooltip="Ex. jane.doe@gmail.com")],

    [sg.Text('')],
    [sg.Text(text='Enter your Gmail App Password:', tooltip="Ex. aljkhwfioicnlnkw"),
     sg.InputText(tooltip="Ex. aljkhwfioicnlnkw")],

    [sg.Text('')],
    [sg.Text(text='Enter the emails of the senders which you want to delete '
                  '\nemail messages from with each email address on a new line:')],

    [sg.Multiline(size=(60, 20), sbar_background_color="grey42", key="email_list")],

    [sg.Button('Start', button_color="springgreen4", disabled=False, disabled_button_color="grey42", key="-START-"),
     sg.Button('Quit', button_color="firebrick4")]
]

# create the output column
outputs_columns = [
    [sg.Text('Progress Updates:')],
    [sg.Output(size=(70, 20),
               font="Consolas 10",
               sbar_background_color="grey42",
               echo_stdout_stderr=True,
               key='log'
               )
     ],

    [sg.ProgressBar(max_value=100,
                    orientation='h',
                    expand_x=True,
                    size=(20, 20),
                    key='-PBAR-')
     ],

    [sg.Text('', key='-OUT-', enable_events=True, justification='center', expand_x=True)]
]


# set up the gui windows layout
layout = [
    [
        sg.Column(inputs_column),
        sg.VSeperator(),
        sg.Column(outputs_columns),
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
window = sg.Window('Gmail Clean-Up Utility', layout, resizable=True)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    # kill the process if user closes window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Quit':
        break

    # turn the list of emails given by the user input into a list
    email_list = values['email_list'].strip().splitlines()



    #     # window["-START-"].update(disabled=False)
    # else:
    #     logging.info("all inputs entered!")

    # checks to ensure the user entered values
    if values[0] == '':
        logging.info("No user email entered. Please enter your email and try again.")
    if values[1] == '':
        logging.info("Gmail App Password not entered. Please enter your password and try again.")
    if not len(email_list) >= 1:
        logging.info("No email sender addresses entered. Please enter at least one sender email and try again.")

    # what to do when the start button is pressed
    if event == "Start":
        if values[0] == '' and values[1] == '' and len(email_list) == 0:
            logging.info("No inputs given yet. All fields must be filled out before you can start the process.")
            window.refresh()

        # disable the start button while the process is running
        window['-START-'].update(disabled=True)

        # Poll queue
        try:
            record = log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = queue_handler.format(record)
            window['-LOG-'].update(msg + '\n', append=True)

        logging.info("Starting Process...")

        # set the max value to the number of sender emails given
        window['-PBAR-'].UpdateBar(max=len(email_list))

        for email in email_list:
            logging.info("")

            for i in range(len(email_list)):
                # update the progress bar
                window['-PBAR-'].UpdateBar(current_count=i + 1)
                window['-OUT-'].update(f"{int(round((((i + 1) / len(email_list)) * 100), 0))}%")

            # run the main delete_emails.py function
            if __name__ == "__main__":
                main(
                    email_address=email,
                    base_user_email=values[0],
                    base_app_password=values[1]
                )
        # re-enable the start button once the process finishes running
        window['-START-'].update(disabled=False)
        logging.info("Process Complete. All Emails Deleted!")

window.close()
