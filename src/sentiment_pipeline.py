# src/sentiment_pipeline.py

# Twitter API and sentiment scoring
import tweepy
from textblob import TextBlob

# Twitter API credentials from .env config
from config import TWITTER_BEARER_TOKEN

# Custom retry decorator (retries on failure)
from src.utils import retry

# ⏳ Fetches recent tweets and returns average sentiment score
@retry(max_attempts=3, delay=2, backoff=2)
def fetch_twitter_sentiment(query="bitcoin OR BTC", max_results=10):
    # Setup Tweepy client using bearer token
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

    # Call Twitter API (v2) to get recent tweets
    response = client.search_recent_tweets(query=query, max_results=max_results)
    sentiments = []

    # If data is returned, process each tweet
    if response.data:
        for tweet in response.data:
            # Analyze sentiment polarity: [-1 = negative, +1 = positive]
            score = TextBlob(tweet.text).sentiment.polarity
            sentiments.append({
                "text": tweet.text,
                "score": score,
                "timestamp": tweet.id  # Optional: you could use created_at for precision
            })

    return sentiments  # ✅ Return all tweet scores individually, not averaged yet
