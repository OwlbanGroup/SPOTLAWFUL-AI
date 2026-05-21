from importlib import import_module

try:
    Client = import_module("twilio.rest").Client
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    Client = None


class SMSCommunication:
    def __init__(self, account_sid, auth_token, from_number):
        self.from_number = from_number
        self.client = Client(account_sid, auth_token) if Client else None

    def send_sms(self, to_number, message):
        if self.client is None:
            print(f"SMS delivery unavailable (twilio not installed). Recipient: {to_number}, message: {message}")
            return {"status": "unavailable", "reason": "twilio not installed"}

        try:
            sent_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            print(f"SMS sent to {to_number}: SID {sent_message.sid}")
            return {"status": "sent", "sid": sent_message.sid}
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return {"status": "failed", "error": str(e)}
