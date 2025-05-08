import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailCommunication:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_address, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_address, text)
            server.quit()
            print(f"Email sent to {to_address} with subject '{subject}'")
        except Exception as e:
            print(f"Failed to send email: {e}")
