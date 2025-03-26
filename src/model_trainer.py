# src/model_trainer.py

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping
import joblib

# Prepares LSTM-compatible windowed dataset
def prepare_data(df, feature_cols, target_col='close', window_size=10):
    df = df.dropna().reset_index(drop=True)

    # Generate binary target: 1 = price goes up next candle, 0 = down
    df['target'] = (df[target_col].shift(-1) > df[target_col]).astype(int)

    features = df[feature_cols].values
    target = df['target'].values

    # Normalize features
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    # Create time-series windows for LSTM
    X, y = [], []
    for i in range(window_size, len(features_scaled)):
        X.append(features_scaled[i-window_size:i])  # Shape: (window_size, num_features)
        y.append(target[i])

    X, y = np.array(X), np.array(y)
    return X, y, scaler  # ✅ Correctly return the fitted scaler

# Builds, trains, and returns the LSTM model
def train_lstm_model(X, y):
    model = Sequential()
    model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1, activation='sigmoid'))  # Binary classification output

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    # 🛡️ Add EarlyStopping to avoid overfitting
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )

    model.fit(
        X,
        y,
        epochs=50,                  # Increased epochs since EarlyStopping handles early exit
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop]
    )

    return model  # Note: scaler is now passed separately from prepare_data()

# Saves model and scaler to disk
def save_model(model, scaler, model_path, scaler_path):
    model.save(model_path)
    joblib.dump(scaler, scaler_path)
    print(f"✅ Model saved: {model_path}")
    print(f"✅ Scaler saved: {scaler_path}")
