import hashlib
import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def read_image_file(file_storage) -> np.ndarray:
    """
    Read an uploaded image file (Flask FileStorage) and return as a BGR OpenCV array.
    """
    data = file_storage.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def preprocess_image(
    image_bgr: np.ndarray,
    target_size: Tuple[int, int] = (128, 128),
) -> np.ndarray:
    """
    Resize and normalize image for CNN input.

    Returns a float32 array of shape (height, width, 3) with values in [0,1].
    """
    resized = cv2.resize(image_bgr, target_size)
    normalized = resized.astype("float32") / 255.0
    return normalized


def compute_image_hash(preprocessed: np.ndarray) -> str:
    """
    Compute a simple SHA256 hash of the preprocessed image.
    This is used as a basic way to detect if we have seen the exact same image before.
    """
    # Ensure deterministic representation.
    data_bytes = preprocessed.tobytes()
    return hashlib.sha256(data_bytes).hexdigest()


def prepare_for_model(preprocessed: np.ndarray) -> np.ndarray:
    """
    Expand a preprocessed image to add the batch dimension expected by Keras.
    """
    return np.expand_dims(preprocessed, axis=0)

