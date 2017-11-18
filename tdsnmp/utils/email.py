import os
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib


class Emailer(object):
    def __init__(self, sender=None, email_server=None, recipient_list=None):
        self.sender = str(sender) if sender is not None else '{}@{}'.format(__name__.split('.')[0], socket.getfqdn())
        self.email_server = str(email_server) if email_server is not None else 'localhost'
        raw_recipient_list = recipient_list if recipient_list is not None else ['usrolh@tdstelecom.com',]
        self.recipient_list = list(raw_recipient_list) if not isinstance(raw_recipient_list, list) else raw_recipient_list

    def send_email(
        self,
        send_to=None,
        subject=None,
        contents=None,
        attachments=None,
        preamble=None,
    ):
        if not send_to is None:
            send_to = self.recipient_list
        if not isinstance(send_to, list):
            send_to = list(send_to)
        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = ", ".join(send_to)
        message['Subject'] = str(subject) if subject is not None else ''
        message.preamble = str(preamble) if preamble is not None else message['Subject']
        message.attach(
            MIMEText(str(contents) if contents is not None else '')
        )
        for attachment in attachments or []:
            with open(attachment, "rb") as file:
                message.attach(
                    MIMEApplication(
                        file.read(),
                        Content_Disposition='attachment; filename="{}"'.format(os.path.basename(attachment)),
                        Name=os.path.basename(attachment)
                    )
                )
        self.send_built_message(message=message)

    def send_built_message(self, message):
        server = smtplib.SMTP(self.email_server)
        try:
            server.send_message(message)
        finally:
            server.quit()
