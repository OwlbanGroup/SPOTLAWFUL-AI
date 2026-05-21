from importlib import import_module

try:
    Client = import_module("twilio.rest").Client
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    Client = None


class PhoneCallCommunication:
    def __init__(self, account_sid, auth_token, from_number):
        self.from_number = from_number
        self.client = Client(account_sid, auth_token) if Client else None

    def make_call(self, to_number, twiml_url):
        """
        Make a phone call to the specified number.
        twiml_url: URL pointing to TwiML instructions for the call.
        """
        if self.client is None:
            print(f"Phone call delivery unavailable (twilio not installed). Recipient: {to_number}, TwiML: {twiml_url}")
            return {"status": "unavailable", "reason": "twilio not installed"}

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=twiml_url
            )
            print(f"Call initiated to {to_number}: SID {call.sid}")
            return {"status": "initiated", "sid": call.sid}
        except Exception as e:
            print(f"Failed to make call: {e}")
            return {"status": "failed", "error": str(e)}
