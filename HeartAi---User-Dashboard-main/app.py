from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import uuid
import time
from heartai import create_inference_and_spectrogram_file

app = Flask(__name__)
CORS(app)

# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MASTER_DB = os.path.join(DATA_FOLDER, 'master.db')
os.makedirs(DATA_FOLDER, exist_ok=True)

def validate_credentials(username, password_md5):
    """
    Validate user credentials and return the user's role.

    Args:
        username (str): The username.
        password_md5 (str): The MD5 hash of the password.

    Returns:
        tuple: A tuple containing the user's role, or None if invalid.
    """
    try:
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            result = cur.execute(
                "SELECT role FROM credentials WHERE username=? AND password_md5=?",
                (username, password_md5)
            ).fetchone()
        return result  # Returns (role,)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

@app.route('/createuser', methods=['POST'])
def create_user():
    """
    API endpoint to create a new user.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        role = data.get('role', 'patient')

        # Create a unique folder for the user
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
    """
    API endpoint for user login.
    """
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
    """
    API endpoint to upload a heartbeat audio file and analyze it.
    """
    try:
        username = request.form.get('username')
        password_md5 = request.form.get('password_md5')
        patient_name = request.form.get('patient_name')

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file data provided'}), 400

        # Save the uploaded file
        epoch = int(time.time())
        folder_name = str(uuid.uuid4())
        user_folder = os.path.join(DATA_FOLDER, folder_name)
        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, f"{epoch}.wav")
        file.save(file_path)

        # Perform analysis on the file
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
    """
    API endpoint to access the analysis history of a user.
    """
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
    """
    API endpoint to view details of a specific analysis record.
    """
    try:
        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if the user is authorized to access the record
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT patient_name, file_path, inference, doctor_notes, username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()

        if row:
            record_username = row[4]
            user_role = validate_credentials(username, password_md5)[0]

            # Allow access if the user owns the record or is a doctor
            if username != record_username and user_role != 'doctor':
                return jsonify({'error': 'Unauthorized access'}), 403

            return jsonify({
                "patient_name": row[0],
                "file_path": row[1],
                "inference": row[2],
                "doctor_notes": row[3]
            }), 200
        else:
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"Error retrieving history details: {e}")
        return jsonify({'error': 'Failed to retrieve history details'}), 500

@app.route('/update_notes/<int:record_id>', methods=['POST'])
def update_notes(record_id):
    """
    API endpoint for doctors to update the doctor's notes of a specific analysis record.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        doctor_notes = data.get('doctor_notes')

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        user_role = validate_credentials(username, password_md5)[0]
        if user_role != 'doctor':
            return jsonify({'error': 'Unauthorized: Only doctors can update notes'}), 403

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            # Check if the record exists
            query = "SELECT username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()

            if not row:
                return jsonify({'error': 'Record not found'}), 404

            record_username = row[0]

            # Ensure the doctor can only update records they have created
            if username != record_username:
                return jsonify({'error': 'Unauthorized: You can only update your own records'}), 403

            # Update the doctor's notes
            cur.execute(
                "UPDATE analysis_history SET doctor_notes=? WHERE id=?",
                (doctor_notes, record_id)
            )
            con.commit()

        return jsonify({'message': 'Notes updated successfully.'}), 200
    except Exception as e:
        print(f"Error updating notes: {e}")
        return jsonify({'error': 'Failed to update notes.'}), 500

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    """
    API endpoint for users to delete their own analysis records.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')

        # Validate user credentials
        role = validate_credentials(username, password_md5)
        if not role:
            return jsonify({'error': 'Invalid credentials'}), 401

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            # Check if the record exists and belongs to the user
            cur.execute("SELECT username FROM analysis_history WHERE id=?", (record_id,))
            row = cur.fetchone()

            if not row:
                return jsonify({'error': 'Record not found'}), 404

            record_username = row[0]
            if record_username != username:
                return jsonify({'error': 'Unauthorized: You can only delete your own records'}), 403

            # Delete the record
            cur.execute("DELETE FROM analysis_history WHERE id=?", (record_id,))
            con.commit()

        return jsonify({'message': 'Record deleted successfully.'}), 200
    except Exception as e:
        print(f"Error deleting record: {e}")
        return jsonify({'error': 'Failed to delete record.'}), 500

if __name__ == '__main__':
    if not os.path.exists(MASTER_DB):
        # Initialize the database if it doesn't exist
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
                    doctor_notes TEXT,
                    FOREIGN KEY (username) REFERENCES credentials (username)
                )"""
            )
            con.commit()
    else:
        # Check if 'doctor_notes' column exists; if not, add it
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute("PRAGMA table_info(analysis_history)")
            columns = [info[1] for info in cur.fetchall()]
            if 'doctor_notes' not in columns:
                cur.execute("ALTER TABLE analysis_history ADD COLUMN doctor_notes TEXT")
                con.commit()
    app.run(host='0.0.0.0', port=8080)
