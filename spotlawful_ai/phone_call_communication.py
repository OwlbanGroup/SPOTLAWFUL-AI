from twilio.rest import Client

class PhoneCallCommunication:
    def __init__(self, account_sid, auth_token, from_number):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def make_call(self, to_number, twiml_url):
        """
        Make a phone call to the specified number.
        twiml_url: URL pointing to TwiML instructions for the call.
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=twiml_url
            )
            print(f"Call initiated to {to_number}: SID {call.sid}")
        except Exception as e:
            print(f"Failed to make call: {e}")
