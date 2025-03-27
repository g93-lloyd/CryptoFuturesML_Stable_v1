# src/sentiment_pipeline.py

import tweepy
from textblob import TextBlob
from src.config import TWITTER_BEARER_TOKEN
from src.utils import retry

# ✅ Toggle this ON/OFF to use real or fallback sentiment
USE_MOCK_SENTIMENT = True  # 🔁 Set to False in real production with a paid API plan

@retry(max_attempts=3, delay=2, backoff=2)
def fetch_twitter_sentiment(query="bitcoin OR BTC", max_results=10):
    if USE_MOCK_SENTIMENT:
        print("⚠️ Twitter sentiment skipped — using fallback neutral sentiment.")
        return [{"timestamp": "mock", "score": 0.0}]

    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        response = client.search_recent_tweets(query=query, max_results=max_results)
        sentiments = []

        if response.data:
            for tweet in response.data:
                score = TextBlob(tweet.text).sentiment.polarity
                sentiments.append({
                    "text": tweet.text,
                    "score": score,
                    "timestamp": tweet.id
                })

        return sentiments if sentiments else [{"timestamp": "empty", "score": 0.0}]

    except Exception as e:
        print(f"❌ Twitter API error: {e}")
        return [{"timestamp": "fallback", "score": 0.0}]

