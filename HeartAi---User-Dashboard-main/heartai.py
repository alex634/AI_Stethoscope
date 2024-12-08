# Import necessary libraries for audio processing and machine learning.
# NumPy for numerical operations.
# Librosa for audio analysis.
# TensorFlow and Keras for model loading and prediction.

import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras.models import load_model
# Import libraries for plotting, image manipulation, and file system operations.
# Matplotlib for creating plots and visualizations.
# PIL (Pillow) for image processing.
# OS module for interacting with the operating system.

import matplotlib.pyplot as plt
from PIL import Image
import os

# Define the base directory for the project.
# Set the path to the saved heart disease prediction model.
# Specify the directory to store generated spectrograms.
# Create the spectrogram directory if it doesn't exist.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_model.h5')
SPECTROGRAM_DIR = os.path.join(BASE_DIR, 'spectrograms')
os.makedirs(SPECTROGRAM_DIR, exist_ok=True)
# Load the pre-trained heart disease prediction model.
# Access and print the expected input shape of the loaded model.
# This ensures the input data will match model requirements.
# Verification step to prevent shape mismatch errors during prediction.


model = load_model(MODEL_PATH)
print("Expected input shape for the model:", model.input_shape)

# Define a function to extract audio features and save as an image.
# Takes input audio file path and desired output image path as arguments.
# Uses librosa to load the audio file with automatic sample rate detection.
# Handles potential errors during audio file loading using a try-except block.

def extract_features(input_Wave_Path, output_Image_Path):
    try:

        audio, sr = librosa.load(input_Wave_Path, sr=None)
        # Compute the mel spectrogram from the loaded audio data.
        # Convert the spectrogram to decibels for better visualization.
        # Create a matplotlib figure to display the spectrogram.
        # Set the figure size for better display quality.

        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        plt.figure(figsize=(5, 5))
        # Display the spectrogram using librosa's display function.
        # Turn off the axis for a cleaner image.
        # Save the spectrogram as an image file.
        # Close the plot to free up resources.

        librosa.display.specshow(spectrogram_db, sr=sr, hop_length=512, cmap='viridis')
        plt.axis('off')
        plt.savefig(output_Image_Path, bbox_inches='tight', pad_inches=0)
        plt.close()
# Define the target size for resizing the spectrogram image.
# Open the saved spectrogram image using PIL.
# Convert the image to grayscale ('L' mode).
# Resize the image to the target dimensions.


        target_size = (128, 128)  
        image = Image.open(output_Image_Path).convert('L').resize(target_size)

        # Normalize the pixel values of the image to the range [0, 1].
        # Add a channel dimension to the image array (for grayscale).
        # Add a batch dimension to the image array for model input compatibility.
        

        image = np.array(image) / 255.0  
        image = np.expand_dims(image, axis=-1)  
        image = np.expand_dims(image, axis=0)  

        # Return the preprocessed image array.
        # Handle exceptions during feature extraction.
        # Print the error message for debugging purposes.
        # Re-raise the exception to halt execution if needed.

        return image
    except Exception as e:
        print("Error in extract_features:", e)
        raise
# Define a function to create an inference and save a spectrogram.
# Takes the path to the input audio wave file as an argument.
# Uses a try-except block for error handling.
# This function encapsulates the entire inference process.


def create_inference_and_spectrogram_file(input_Wave_Path):
    try:

        # Construct the output image path from the input wave file path.
        # Extract features from the audio file and save the spectrogram.
        # Perform prediction using the loaded model on extracted features.
        # Extract the prediction probability from the model's output.

        image_Path = input_Wave_Path.replace(".wav", ".png")
        features = extract_features(input_Wave_Path, image_Path)

        prediction = model.predict(features)[0][0]
        # Assign a label based on the prediction probability threshold.
        # Create a text file to store the inference result.
        # Write the predicted label ('Present' or 'Absent') to the file.
        # Close the file to save changes and release resources.

        label = 'Present' if prediction > 0.5 else 'Absent'
        inference_Result_File = open(input_Wave_Path.replace(".wav", ".txt"), "w")
        inference_Result_File.write(label)
        inference_Result_File.close()
        # Return the predicted label.
        # Handle any exceptions during the inference process.
        # Print detailed error messages for debugging.
        # Re-raise the exception to stop execution if necessary.

        return label
    except Exception as e:
        print("Error in create_inference_and_spectrogram_file:", e)
        raise
