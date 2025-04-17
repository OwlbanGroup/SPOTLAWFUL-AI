from transformers import pipeline

# Load sentiment-analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Example text for analysis
text = "SPOTLAWFUL AI is transforming the legal industry!"

# Perform sentiment analysis
result = sentiment_analyzer(text)

# Print the result
print("Sentiment Analysis Result:", result)
