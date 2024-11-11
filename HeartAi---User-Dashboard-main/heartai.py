import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from PIL import Image
import os

# Set TensorFlow to CPU-only mode to avoid GPU dependency issues
#tf.config.set_visible_devices([], 'GPU')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_model.h5')
SPECTROGRAM_DIR = os.path.join(BASE_DIR, 'spectrograms')
os.makedirs(SPECTROGRAM_DIR, exist_ok=True)

# Load the model and confirm expected input shape
model = load_model(MODEL_PATH)
print("Expected input shape for the model:", model.input_shape)

def extract_features(file_path):
    try:
        # Load audio file and generate mel spectrogram
        audio, sr = librosa.load(file_path, sr=None)
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        # Save the spectrogram as an image
        image_path = os.path.join(SPECTROGRAM_DIR, os.path.basename(file_path).replace('.wav', '.png'))
        plt.figure(figsize=(5, 5))
        librosa.display.specshow(spectrogram_db, sr=sr, hop_length=512, cmap='viridis')
        plt.axis('off')
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Resize the image to 128x128 and convert to RGB to match the model's expected input
        target_size = (128, 128)  # Model expects 128x128 RGB images
        image = Image.open(image_path).convert('RGB').resize(target_size)

        # Convert to a NumPy array, normalize, and add batch dimension
        image = np.array(image) / 255.0  # Normalize pixel values to [0, 1]
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        return image, image_path
    except Exception as e:
        print("Error in extract_features:", e)
        raise  # Re-raise the error to be handled in predict_heart_condition

def predict_heart_condition(file_path):
    try:
        # Extract features and image path
        features, image_path = extract_features(file_path)

        # Predict using the model
        prediction = model.predict(features)[0][0]
        label = 'Abnormal' if prediction > 0.5 else 'Normal'

        return {'prediction': label, 'spectrogram_image': image_path}
    except Exception as e:
        print("Error in predict_heart_condition:", e)
        raise  # This will propagate the error to app.py
