import datetime
import os
import base64
import mimetypes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from loguru import logger


sender_email = 'dev.kartikaggarwal117@gmail.com'

target_email_list = [
    'dev.kartikaggarwal117@gmail.com',
    'kartik.aggarwal117@gmail.com',
    'ecom1@novuslifesciences.com',
    'ecom3@novuslifesciences.com',
    'ecom4@novuslifesciences.com',
    'ecom7@novuslifesciences.com',
    'ecom8@novuslifesciences.com',
    'ecom9@novuslifesciences.com',
    'ecom10@novuslifesciences.com',
    'ecom11@novuslifesciences.com',
    'ecom12@novuslifesciences.com',
    'ecom13@novuslifesciences.com',
    'ecom14@novuslifesciences.com',
    'ecom15@novuslifesciences.com',
    'ecom16@novuslifesciences.com',
    'ecom17@novuslifesciences.com',
    'ecom18@novuslifesciences.com',
    'ecom19@novuslifesciences.com',
    'ecom20@novuslifesciences.com',
]
# target_email_list = [
#     'dev.kartikaggarwal117@gmail.com',
#     'kartik.aggarwal117@gmail.com',
# ]


def get_credentials():
    creds = None
    if os.path.exists('data/auth/token.json'):
        creds = Credentials.from_authorized_user_file('data/auth/token.json')
        creds.refresh(Request())
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/auth/client_secret.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/gmail.send']
            )
            creds = flow.run_local_server(port=0)
        with open('data/auth/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def send_email(sender, to_list, subject, message_text, file_paths=[]):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    message = create_message(sender, to_list, subject, message_text, file_paths)
    
    try:
        message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        logger.debug('Email has been sent successfully')
        return message
    except Exception as e:
        logger.error(f'An error occurred while sending out email: {e}')
        return None


def create_message(sender, to_list, subject, message_text, file_paths=[]):
    message = MIMEMultipart()
    message['from'] = sender
    message['to'] = ', '.join(to_list)
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    for file_path in file_paths:
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        with open(file_path, 'rb') as file:
            part = MIMEBase(main_type, sub_type)
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=file_path.split('/')[-1])
        message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    return {'raw': raw_message}


def send_output_mail():
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%d %B")
    send_email(sender_email, 
               target_email_list, 
               f'{formatted_date} - Review Sheet', 
               'This email has been automatically generated!\n\nPlease find the Review Sheet and Script Logs attached.', 
               ['data/output.xlsx', 'logs/script.log'])


def send_error_mail(error):
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%d %B")
    send_email(sender_email, 
               target_email_list, 
               f'{formatted_date} - Error while running REVIEW MONITORING script', 
               f'THIS EMAIL HAS BEEN AUTOMATICALLY GENERATED!\n\nA critical error has occured while running the script: "{error}".\nA copy of this email has been sent to the developer.\nPlease contact the developer for further information.\nScript logs have been attached.', 
               ['logs/script.log'])
