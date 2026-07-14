import os
import smtplib
from email.message import EmailMessage


class ConsoleNotifier:
    def send(self, subject: str, body: str, recipient: str) -> None:
        line = "=" * 56
        print(f"\n{line}\nTO: {recipient}\nALERT: {subject}\n{line}\n{body}\n{line}\n")


class EmailNotifier:
    def __init__(self):
        self.host = os.environ["SMTP_HOST"]
        self.port = int(os.environ["SMTP_PORT"])
        self.user = os.environ["SMTP_USER"]
        self.password = os.environ["SMTP_PASSWORD"]

    def send(self, subject: str, body: str, recipient: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.user
        message["To"] = recipient
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(message)
        print(f"Emailed alert to {recipient}: {subject}")