from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import os
import traceback
import sqlite3
import hashlib
import uuid
import librosa
import librosa.display
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MASTER_DB = os.path.join(DATA_FOLDER, 'master.db')

# Ensure required folders exist
os.makedirs(DATA_FOLDER, exist_ok=True)

# Initialize the database
def initialize_database():
    with sqlite3.connect(MASTER_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                username TEXT PRIMARY KEY,
                password_md5 CHAR(32),
                folder_name TEXT
            )
        ''')
        conn.commit()

initialize_database()

# Utility to hash passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')

        with sqlite3.connect(MASTER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT folder_name FROM credentials WHERE username = ? AND password_md5 = ?',
                (username, password_md5)
            )
            result = cursor.fetchone()

        if result:
            return jsonify({"success": True, "folder_name": result[0]}), 200
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Create user route
@app.route('/createuser', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')

        folder_name = str(uuid.uuid4())  # Generate a unique folder name
        os.makedirs(os.path.join(DATA_FOLDER, folder_name), exist_ok=True)

        with sqlite3.connect(MASTER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO credentials (username, password_md5, folder_name) VALUES (?, ?, ?)',
                (username, password_md5, folder_name)
            )
            conn.commit()

        return jsonify({"success": True}), 200
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        data = request.form
        username = data.get('username')
        password_md5 = data.get('password_md5')

        with sqlite3.connect(MASTER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT folder_name FROM credentials WHERE username = ? AND password_md5 = ?',
                (username, password_md5)
            )
            result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Invalid credentials"}), 401

        folder_name = result[0]
        user_folder = os.path.join(DATA_FOLDER, folder_name)
        file_path = os.path.join(user_folder, file.filename)
        file.save(file_path)

        # Process the uploaded file (e.g., generate spectrogram)
        audio, sr = librosa.load(file_path, sr=None)
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        spectrogram_path = file_path.replace('.wav', '_spectrogram.png')
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='mel', cmap='magma')
        plt.colorbar(format='%+2.0f dB')
        plt.title(f"Spectrogram of {file.filename}")
        plt.tight_layout()
        plt.savefig(spectrogram_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        return jsonify({
            "success": True,
            "spectrogram_image_url": spectrogram_path
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Access history route
@app.route('/accesshistory', methods=['GET'])
def access_history():
    try:
        data = request.get_json()
        username = data.get("username")
        password_md5 = data.get("password_md5")
        if not validate_credentials(username, password_md5):
            return jsonify({"error": "Invalid credentials"}), 401

        user_folder = get_user_folder(username)
        folder_path = os.path.join(DATA_FOLDER, user_folder)
        epochs = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith(".wav") or file.endswith(".flac"):
                    epochs.append(file)
        
        return jsonify({"folder": user_folder, "epochs": sorted(epochs, reverse=True)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
