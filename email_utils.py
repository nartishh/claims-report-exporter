import smtplib
import os
from email.message import EmailMessage
import logging

class EmailSender:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.server = smtp_server
        self.port = smtp_port
        self.user = smtp_user
        self.password = smtp_password

    def send(self, file_path, email_from, email_to, subject, body):
        msg = EmailMessage()
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Subject"] = subject
        msg.set_content(body)

        with open(file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(f.name)

        msg.add_attachment(file_data,
                        maintype="application",
                        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=file_name)
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            logging.info("Email sent successfully!")
        except Exception:
            logging.exception("Error occured while sending email")