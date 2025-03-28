# src/model_trainer.py

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping
import joblib

# ✅ Prepares the dataset for LSTM input by creating sliding windows
def prepare_data(df, feature_cols, target_col='close', window_size=10):
    df = df.dropna().reset_index(drop=True)

    # 🟡 Define binary target: 1 if next candle is higher, else 0
    df['target'] = (df[target_col].shift(-1) > df[target_col]).astype(int)

    # 🧪 Extract features and target
    features = df[feature_cols].values
    target = df['target'].values

    # 📏 Normalize features using MinMaxScaler
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    # 🎛️ Create sequences for LSTM
    X, y = [], []
    for i in range(window_size, len(features_scaled)):
        X.append(features_scaled[i-window_size:i])
        y.append(target[i])

    return np.array(X), np.array(y), scaler

# 🧠 Builds and trains an LSTM model
def train_lstm_model(X, y):
    model = Sequential()
    model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # ⏹️ Early stopping to prevent overfitting
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    model.fit(
        X, y,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop]
    )

    return model

# 💾 Saves the trained model and scaler
def save_model(model, scaler, model_path, scaler_path):
    print("🚨 DEBUG: save_model() called")
    print(f"🚨 model_path type: {type(model_path)}")
    print(f"🚨 model_path value: {model_path}")
    
    assert model_path.endswith(".keras"), "❌ Model path is not using .keras format!"

    model.save(model_path)
    joblib.dump(scaler, scaler_path)
    print(f"✅ Model saved: {model_path}")
    print(f"✅ Scaler saved: {scaler_path}")


