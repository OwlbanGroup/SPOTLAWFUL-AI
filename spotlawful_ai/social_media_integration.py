import requests

class SocialMediaIntegration:
    def __init__(self, platform, access_token):
        self.platform = platform.lower()
        self.access_token = access_token
        self.api_url = self.get_api_url()

    def get_api_url(self):
        if self.platform == 'twitter':
            return 'https://api.twitter.com/2'
        elif self.platform == 'facebook':
            return 'https://graph.facebook.com/v12.0'
        elif self.platform == 'linkedin':
            return 'https://api.linkedin.com/v2'
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def post_update(self, message):
        if self.platform == 'twitter':
            return self.post_twitter_update(message)
        elif self.platform == 'facebook':
            return self.post_facebook_update(message)
        elif self.platform == 'linkedin':
            return self.post_linkedin_update(message)

    def post_twitter_update(self, message):
        url = f"{self.api_url}/tweets"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'text': message
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print("Tweet posted successfully.")
        else:
            print(f"Failed to post tweet: {response.text}")
        return response

    def post_facebook_update(self, message):
        url = f"{self.api_url}/me/feed"
        params = {
            'message': message,
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            print("Facebook post created successfully.")
        else:
            print(f"Failed to create Facebook post: {response.text}")
        return response

    def post_linkedin_update(self, message):
        # LinkedIn API requires more complex setup; simplified example
        url = f"{self.api_url}/ugcPosts"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        payload = {
            "author": "urn:li:person:YOUR_PERSON_URN",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print("LinkedIn post created successfully.")
        else:
            print(f"Failed to create LinkedIn post: {response.text}")
        return response
