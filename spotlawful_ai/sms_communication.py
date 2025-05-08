from twilio.rest import Client

class SMSCommunication:
    def __init__(self, account_sid, auth_token, from_number):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(self, to_number, message):
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            print(f"SMS sent to {to_number}: SID {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")
