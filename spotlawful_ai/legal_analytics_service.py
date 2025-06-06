class LegalAnalyticsService:
    def __init__(self, ai_model, subscription_manager):
        self.ai_model = ai_model
        self.subscription_manager = subscription_manager

    def provide_insights(self, user_id, legal_text):
        if not self.subscription_manager.is_subscribed(user_id):
            raise PermissionError("User does not have an active subscription.")
        insights = self.ai_model.parse(legal_text)
        return insights

class SubscriptionManager:
    def __init__(self):
        self.active_subscriptions = set()

    def subscribe(self, user_id):
        self.active_subscriptions.add(user_id)

    def unsubscribe(self, user_id):
        self.active_subscriptions.discard(user_id)

    def is_subscribed(self, user_id):
        return user_id in self.active_subscriptions
