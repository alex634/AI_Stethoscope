from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import uuid
import time
from heartai import create_inference_and_spectrogram_file

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MASTER_DB = os.path.join(DATA_FOLDER, 'master.db')
os.makedirs(DATA_FOLDER, exist_ok=True)


def validate_credentials(username, password_md5):
    try:
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            result = cur.execute(
                "SELECT role FROM credentials WHERE username=? AND password_md5=?",
                (username, password_md5)
            ).fetchone()
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


@app.route('/createuser', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        role = data.get('role', 'patient')

        folder_name = str(uuid.uuid4())
        os.makedirs(os.path.join(DATA_FOLDER, folder_name), exist_ok=True)

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO credentials (username, password_md5, folder_name, role) VALUES (?, ?, ?, ?)",
                (username, password_md5, folder_name, role)
            )
            con.commit()
        return jsonify({'success': True}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'error': 'Failed to create user'}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        role = validate_credentials(username, password_md5)

        if role:
            return jsonify({"username": username, "role": role[0]}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({'error': 'Failed to log in'}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        username = request.form.get('username')
        password_md5 = request.form.get('password_md5')
        patient_name = request.form.get('patient_name')

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file data provided'}), 400

        epoch = int(time.time())
        folder_name = str(uuid.uuid4())
        user_folder = os.path.join(DATA_FOLDER, folder_name)
        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, f"{epoch}.wav")
        file.save(file_path)

        inference_result = create_inference_and_spectrogram_file(file_path)

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO analysis_history (username, epoch, file_path, inference, patient_name) VALUES (?, ?, ?, ?, ?)",
                (username, epoch, file_path, inference_result, patient_name)
            )
            con.commit()

        return jsonify({'epoch': epoch, 'inference': inference_result}), 200
    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify({'error': 'Failed to process the file'}), 500


@app.route('/accesshistory', methods=['GET'])
def access_history():
    try:
        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT id, patient_name, epoch FROM analysis_history WHERE username=? ORDER BY epoch DESC"
            rows = cur.execute(query, (username,)).fetchall()

        result = [{"id": row[0], "patient_name": row[1], "epoch": row[2]} for row in rows]
        return jsonify(result), 200
    except Exception as e:
        print(f"Error retrieving access history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500


@app.route('/history/<int:record_id>', methods=['GET'])
def view_history(record_id):
    try:
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT patient_name, file_path, inference FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()

        if row:
            return jsonify({"patient_name": row[0], "file_path": row[1], "inference": row[2]}), 200
        else:
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"Error retrieving history details: {e}")
        return jsonify({'error': 'Failed to retrieve history details'}), 500


if __name__ == '__main__':
    if not os.path.exists(MASTER_DB):
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute(
                """CREATE TABLE credentials (
                    username TEXT PRIMARY KEY,
                    password_md5 TEXT NOT NULL,
                    folder_name TEXT NOT NULL,
                    role TEXT NOT NULL
                )"""
            )
            cur.execute(
                """CREATE TABLE analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    inference TEXT NOT NULL,
                    patient_name TEXT NOT NULL,
                    FOREIGN KEY (username) REFERENCES credentials (username)
                )"""
            )
            con.commit()
    app.run(host='0.0.0.0', port=8080)
