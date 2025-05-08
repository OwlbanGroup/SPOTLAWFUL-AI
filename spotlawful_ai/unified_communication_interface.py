from spotlawful_ai.email_communication import EmailCommunication
from spotlawful_ai.sms_communication import SMSCommunication
from spotlawful_ai.phone_call_communication import PhoneCallCommunication
from spotlawful_ai.social_media_integration import SocialMediaIntegration

class UnifiedCommunicationInterface:
    def __init__(self, email_config, sms_config, phone_config, social_config):
        self.email_comm = EmailCommunication(**email_config)
        self.sms_comm = SMSCommunication(**sms_config)
        self.phone_comm = PhoneCallCommunication(**phone_config)
        self.social_comm = SocialMediaIntegration(**social_config)
        self.user_preferences = {}  # user_id -> preferences dict

    def set_user_preferences(self, user_id, preferences):
        """
        preferences: dict with keys like 'email', 'sms', 'phone', 'social' and boolean values
        """
        self.user_preferences[user_id] = preferences

    def send_message(self, user_id, message, subject=None, twiml_url=None):
        prefs = self.user_preferences.get(user_id, {})
        results = {}

        if prefs.get('email', False) and subject:
            results['email'] = self.email_comm.send_email(user_id, subject, message)

        if prefs.get('sms', False):
            results['sms'] = self.sms_comm.send_sms(user_id, message)

        if prefs.get('phone', False) and twiml_url:
            results['phone'] = self.phone_comm.make_call(user_id, twiml_url)

        if prefs.get('social', False):
            results['social'] = self.social_comm.post_update(message)

        return results
