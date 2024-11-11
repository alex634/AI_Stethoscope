from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import traceback
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import librosa
import librosa.display
from heartai import predict_heart_condition  # Import your prediction function

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow cross-origin requests from Streamlit

# Set up folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ANALYZED_FOLDER = os.path.join(BASE_DIR, 'analyzed_spectrograms')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANALYZED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Backend is running"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded or no filename provided"}), 400

    # Save the uploaded file to the uploads folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Run the heart sound prediction
        prediction_result = predict_heart_condition(file_path)

        # Generate and save spectrogram directly in the analyzed folder
        analyzed_path = create_spectrogram(file_path, file.filename)

        # Include the prediction and the spectrogram URL in the response
        return jsonify({
            "prediction": prediction_result.get("prediction", "Unknown"),
            "spectrogram_image_url": f"/download/{file.filename.replace('.wav', '_analyzed.png')}"
        }), 200
    except Exception as e:
        # Log the error details
        error_message = "An error occurred during prediction"
        print(error_message, e)
        traceback.print_exc()
        return jsonify({"error": error_message, "details": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    analyzed_path = os.path.join(ANALYZED_FOLDER, filename)
    if not os.path.exists(analyzed_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(analyzed_path, mimetype='image/png')

def create_spectrogram(file_path, filename):
    # Load the audio file
    audio, sr = librosa.load(file_path, sr=None)

    # Generate the mel spectrogram
    spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
    spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

    # Save the spectrogram as an image directly in the analyzed folder
    analyzed_path = os.path.join(ANALYZED_FOLDER, filename.replace('.wav', '_analyzed.png'))
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='mel', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f"Spectrogram of {filename}")
    plt.tight_layout()
    plt.savefig(analyzed_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return analyzed_path

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
