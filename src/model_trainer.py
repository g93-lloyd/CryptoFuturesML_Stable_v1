# src/model_trainer.py

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os

# Prepares LSTM-compatible dataset
def prepare_data(df, feature_cols, target_col='close', window_size=10):
    df = df.dropna().reset_index(drop=True)
    df['target'] = (df[target_col].shift(-1) > df[target_col]).astype(int)

    features = df[feature_cols].values
    target = df['target'].values

    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    X, y = [], []
    for i in range(window_size, len(features_scaled)):
        X.append(features_scaled[i - window_size:i])
        y.append(target[i])

    return np.array(X), np.array(y), scaler

# Trains and returns the LSTM model
def train_lstm_model(X, y):
    model = Sequential()
    model.add(Input(shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(64))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    # ✅ Optional .keras checkpoint during training
    checkpoint_path = "models/temp_training_checkpoint.keras"
    model_checkpoint = ModelCheckpoint(
        filepath=checkpoint_path,
        monitor='val_loss',
        save_best_only=True,
        save_format="keras",
        verbose=1
    )

    model.fit(
        X, y,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop, model_checkpoint]
    )

    # Optional: remove temp checkpoint after training
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    return model

# Saves model in .keras format and logs path
def save_model(model, scaler, model_path, scaler_path):
    print("🚨 DEBUG: save_model() called")
    print(f"🚨 model_path received: {model_path}")
    assert model_path.endswith(".keras"), f"❌ ERROR: model_path must end in .keras — received: {model_path}"

    try:
        model.save(model_path, save_format="keras")
        joblib.dump(scaler, scaler_path)

        print(f"✅ Model saved: {model_path}")
        print(f"✅ Scaler saved: {scaler_path}")

    except Exception as e:
        print(f"❌ Failed to save model: {e}")
        raise
