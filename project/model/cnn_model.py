from pathlib import Path
from typing import Optional

import tensorflow as tf
from tensorflow.keras import layers, models


MODEL_PATH = Path(__file__).resolve().parent / "saved_model.keras"


def build_cnn_model(input_shape=(128, 128, 3), num_classes: int = 10) -> tf.keras.Model:
    """
    Define a simple CNN suitable as a starting point for animal image classification.

    For this starter project, the model is untrained and primarily serves as a scaffold.
    """
    model = models.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model


def load_or_build_model() -> tf.keras.Model:
    """
    Attempt to load a previously saved model; otherwise build a fresh untrained CNN.
    """
    if MODEL_PATH.exists():
        return tf.keras.models.load_model(MODEL_PATH)
    return build_cnn_model()


def predict_embedding(model: tf.keras.Model, batch_image) -> Optional[list]:
    """
    For a real system you might want to use an intermediate layer as an embedding.
    Here we simply return the softmax output as a generic 'feature vector'.
    """
    try:
        preds = model.predict(batch_image, verbose=0)
        return preds[0].tolist()
    except Exception:
        # In any error case, return None so callers can handle gracefully.
        return None

