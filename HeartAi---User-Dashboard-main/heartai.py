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

def extract_features(input_Wave_Path, output_Image_Path):
    try:
        # Load audio file and generate mel spectrogram
        audio, sr = librosa.load(input_Wave_Path, sr=None)
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        # Save the spectrogram as an image
        plt.figure(figsize=(5, 5))
        librosa.display.specshow(spectrogram_db, sr=sr, hop_length=512, cmap='viridis')
        plt.axis('off')
        plt.savefig(output_Image_Path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Resize the image to 128x128 and convert to RGB to match the model's expected input
        target_size = (128, 128)  # Model expects 128x128 RGB images
        image = Image.open(output_Image_Path).convert('RGB').resize(target_size)

        # Convert to a NumPy array, normalize, and add batch dimension
        image = np.array(image) / 255.0  # Normalize pixel values to [0, 1]
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        return image
    except Exception as e:
        print("Error in extract_features:", e)
        raise  # Re-raise the error to be handled in predict_heart_condition

#This takes in an input wave file and will create the associated png spectrogram and inference result txt file
def create_inference_and_spectrogram_file(input_Wave_Path):
	try:
		# Extract features and image path
		image_Path = input_Wave_Path.replace(".wav", ".png")
		
		features = extract_features(input_Wave_Path, image_Path)

		# Predict using the model
		prediction = model.predict(features)[0][0]
		label = 'Present' if prediction > 0.5 else 'Absent'
		inference_Result_File = open(input_Wave_Path.replace(".wav", ".txt"), "w")
		inference_Result_File.write(label)
		inference_Result_File.close()
	except Exception as e:
		print("Error in predict_heart_condition:", e)
		raise  # This will propagate the error to app.py
