# Imports technical indicator library (pandas_ta)
import pandas_ta as ta

# 📈 Adds RSI, EMA, and MACD indicators to your OHLCV DataFrame
def add_technical_indicators(df):
    df = df.copy()  # Avoid modifying the original DataFrame in place

    # Add RSI with 14-period window (RSI_14)
    df["rsi_14"] = ta.rsi(df["close"], length=14)

    # Add 21-period EMA (Exponential Moving Average)
    df["ema_21"] = ta.ema(df["close"], length=21)

    # Add MACD (includes macd, signal, histogram)
    macd = ta.macd(df["close"])
    if macd is not None:
        df["macd"] = macd["MACD_12_26_9"]

    return df  # Returns a DataFrame with new technical columns

# 🧠 Merges sentiment score into the same DataFrame
def merge_sentiment(df, sentiment_scores):
    if not sentiment_scores:
        df["sentiment"] = 0  # Default if no sentiment data
        return df
    
    # Average the sentiment score from recent tweets
    avg_score = sum(score["score"] for score in sentiment_scores) / len(sentiment_scores)

    # Add a single sentiment score across all rows (simple but effective)
    df["sentiment"] = avg_score

    return df
