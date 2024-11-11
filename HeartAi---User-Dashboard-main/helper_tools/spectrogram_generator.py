import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

BASE_DIR = '/content/HeartSoundAnalysis'
SOURCE_DIR = os.path.join(BASE_DIR, 'dataset')
DEST_DIR = os.path.join(BASE_DIR, 'spectrograms')
os.makedirs(DEST_DIR, exist_ok=True)

def generate_spectrograms():
    for file in os.listdir(SOURCE_DIR):
        if file.endswith('.wav'):
            audio_path = os.path.join(SOURCE_DIR, file)
            
            # Load the audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Generate the Mel spectrogram
            spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
            spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)
            
            # Plot the spectrogram and save as a .png file
            plt.figure(figsize=(5, 5))
            librosa.display.specshow(spectrogram_db, sr=sr, hop_length=512, x_axis='time', y_axis='mel')
            plt.axis('off')  # Hide axes for a cleaner image
            save_path = os.path.join(DEST_DIR, file.replace('.wav', '.png'))
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close()

generate_spectrograms()
