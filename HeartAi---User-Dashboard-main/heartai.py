# Import necessary libraries for audio processing and machine learning.
# NumPy for numerical operations.
# Librosa for audio analysis.
# TensorFlow and Keras for model loading and prediction.
# Use a non-interactive matplotlib backend (Agg) to avoid GUI issues.

import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import numpy as np
import librosa
import librosa.display  # Added to enable spectrogram plotting with librosa
import tensorflow as tf
from tensorflow.keras.models import load_model
# Import libraries for plotting, image manipulation, and file operations.
# Matplotlib for plotting.
# PIL (Pillow) for image handling.
# OS for file system interactions.

import matplotlib.pyplot as plt
from PIL import Image
import os

# Define the base directory for the project, model path, and spectrogram directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_model.h5')
SPECTROGRAM_DIR = os.path.join(BASE_DIR, 'spectrograms')
os.makedirs(SPECTROGRAM_DIR, exist_ok=True)

# Load the pre-trained heart disease prediction model and print the expected input shape.
model = load_model(MODEL_PATH)
print("Expected input shape for the model:", model.input_shape)

def extract_features(input_Wave_Path, output_Image_Path):
    """
    Convert a .wav audio file into a mel spectrogram image, then preprocess it.
    Steps:
    - Load audio (no resampling, keep original sr).
    - Compute mel spectrogram, convert to dB.
    - Plot and save the spectrogram as an image.
    - Resize image to 128x128, convert to grayscale, normalize pixel values.
    - Add batch and channel dimensions for model input.
    """
    try:
        audio, sr = librosa.load(input_Wave_Path, sr=None)
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        plt.figure(figsize=(5, 5))
        librosa.display.specshow(spectrogram_db, sr=sr, hop_length=512, cmap='viridis')
        plt.axis('off')
        plt.savefig(output_Image_Path, bbox_inches='tight', pad_inches=0)
        plt.close()

        target_size = (128, 128)
        image = Image.open(output_Image_Path).convert('L').resize(target_size)
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=-1)  # Channel dimension
        image = np.expand_dims(image, axis=0)   # Batch dimension
        return image
    except Exception as e:
        print("Error in extract_features:", e)
        raise

def create_inference_and_spectrogram_file(input_Wave_Path):
    """
    Generate a spectrogram from the input .wav, run the model to predict 'Present' or 'Absent',
    and write the result to a .txt file.
    """
    try:
        image_Path = input_Wave_Path.replace(".wav", ".png")
        features = extract_features(input_Wave_Path, image_Path)
        prediction = model.predict(features)[0][0]
        label = 'Present' if prediction > 0.5 else 'Absent'
        with open(input_Wave_Path.replace(".wav", ".txt"), "w") as inference_Result_File:
            inference_Result_File.write(label)
        return label
    except Exception as e:
        print("Error in create_inference_and_spectrogram_file:", e)
        raise
