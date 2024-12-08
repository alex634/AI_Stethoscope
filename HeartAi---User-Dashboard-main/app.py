# Import necessary libraries for Flask application
# Enable Cross-Origin Resource Sharing (CORS)
# Import the os module for file system operations
# Import the sqlite3 module for database interaction

from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import os
import sqlite3
# Import uuid module for unique identifier generation
# Import time module for time-related operations
# Import create_inference_and_spectrogram_file from heartai library
# Import necessary modules for audio processing and inference

import uuid
import time
from heartai import create_inference_and_spectrogram_file

# Initialize Flask application
# Enable CORS for the application
# Comment indicating the purpose of the following code block
# Define base directory paths for the application

app = Flask(__name__)
CORS(app)

# Define base directories
# Start of function definition
# Function to locate the data folder
# Determine the absolute path of the current directory
# Helper function for path management


# Function to find the data folder
def find_data_folder():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # Loop until data folder is found
    # Construct potential path to data folder
    # Check if the potential path is a directory
    # Return the path if directory exists

    while True:
        potential_data_folder = os.path.join(current_dir, 'HeartAi---User-Dashboard-main', 'data')
        if os.path.isdir(potential_data_folder):
            return potential_data_folder
        # Get the parent directory path
        # Check if parent directory is the same as current
        # Break loop if root directory is reached
        # Handle case where root directory is found

        parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
        if parent_dir == current_dir:
            # Reached the root directory
            break
        # Update current directory to parent directory
        # Raise exception if data folder not found
        # Begin try block for exception handling
        # Try to find the data folder

        current_dir = parent_dir
    raise FileNotFoundError("Data folder 'HeartAi---User-Dashboard-main\\data' not found.")

try:
    # Call the function to find the data folder
    # Print the path of the found data folder
    # Handle FileNotFoundError exception
    # Print error message if data folder not found

    DATA_FOLDER = find_data_folder()
    print(f"DATA_FOLDER set to: {DATA_FOLDER}")
except FileNotFoundError as e:
    print(e)
    # Set a default data folder path if not found
    # Create the default data folder if it doesn't exist
    # Print confirmation of default data folder path
    # Handle the case where the data folder is missing

    # If the data folder is not found, set it to a default path
    DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    os.makedirs(DATA_FOLDER, exist_ok=True)
    print(f"DATA_FOLDER set to default: {DATA_FOLDER}")
# Define the path to the master database file
# Function definition: validate user credentials
# Takes username and MD5-hashed password as input
# Checks if credentials match those in database


MASTER_DB = os.path.join(DATA_FOLDER, 'master.db')

def validate_credentials(username, password_md5):
    # Function to validate user credentials
    # Takes username and MD5-hashed password as input
    # Returns user's role if credentials are valid
    # Raises exception if credentials are invalid or database error occurs

    try:
        with sqlite3.connect(MASTER_DB) as con:
            # Create a database cursor object
            # Execute SQL query to fetch user role
            # Query parameters are username and password hash
            # SQL query to check credentials

            cur = con.cursor()
            result = cur.execute(
                "SELECT role FROM credentials WHERE username=? AND password_md5=?",
                (username, password_md5)
            # Fetch the first matching row from the query result
            # Return the fetched role if found
            # Handle potential SQLite errors
            # Print any database error encountered

            ).fetchone()
        return result  # Returns (role,)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # Return None if no matching credentials are found
        # Define a Flask route for user creation
        # Route handles POST requests
        # Function to handle new user creation

        return None

@app.route('/createuser', methods=['POST'])
def create_user():
    # Function docstring: API endpoint for user creation
    # Begin try-except block for error handling
    # Handle potential exceptions during user creation
    # Try block for creating a new user

    try:
        # Get JSON data from the request
        # Extract username from JSON data
        # Extract MD5-hashed password from JSON data
        # Extract user role, defaulting to 'patient'

        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        role = data.get('role', 'patient')
# Generate a UUID for the user's folder
# Create a unique directory for the user's data
# Handle potential errors during directory creation
# Ensure directory creation doesn't fail if it exists


        # Create a unique folder for the user
        folder_name = str(uuid.uuid4())
        os.makedirs(os.path.join(DATA_FOLDER, folder_name), exist_ok=True)
# Establish a connection to the SQLite database
# Create a cursor object for database operations
# Execute an SQL statement to insert new user data
# Begin database transaction to add new user


        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute(
                # SQL query to insert a new user into the database
                # Parameters for the SQL INSERT statement
                # Execute the insertion query
                # Commit changes to the database

                "INSERT INTO credentials (username, password_md5, folder_name, role) VALUES (?, ?, ?, ?)",
                (username, password_md5, folder_name, role)
            )
            con.commit()
        # Return success message with HTTP status code 200
        # Handle unique constraint violation on username
        # Handle other potential exceptions during user creation
        # Return error message with HTTP status code 400

        return jsonify({'success': True}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        # Log the exception details for debugging
        # Return an error message with HTTP status code 500
        # Define a Flask route for user login
        # Route handles POST requests for login

        print(f"Error creating user: {e}")
        return jsonify({'error': 'Failed to create user'}), 500

@app.route('/login', methods=['POST'])
# Function definition for user login
# API endpoint for user authentication
# Function to handle user login requests
# Docstring describing the function's purpose

def login():
    """
    API endpoint for user login.
    """
    # Begin a try-except block for error handling
    # Retrieve JSON data from the request
    # Extract username from the JSON data
    # Extract the MD5 hashed password

    try:
        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')
        # Validate user credentials using the database
        # Check if credentials are valid
        # Return user details and HTTP status code 200 if valid
        # Handle successful login

        role = validate_credentials(username, password_md5)

        if role:
            return jsonify({"username": username, "role": role[0]}), 200
        # Return error message for invalid credentials
        # Handle any exceptions during login process
        # Log the exception details for debugging
        # Return error message with HTTP status code 401

        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during login: {e}")
        # Return error message and HTTP status code 500
        # Define a Flask route for file uploads
        # Route handles POST requests for file uploads
        # Function to handle file upload requests

        return jsonify({'error': 'Failed to log in'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    # Function docstring: API endpoint for audio upload and analysis
    # Begin a try-except block for error handling
    # Handle potential exceptions during file processing
    # Try block for processing the uploaded audio file

    try:
        # Get username from the form data
        # Get MD5-hashed password from the form data
        # Get patient name from the form data
        # Extract relevant information from the request

        username = request.form.get('username')
        password_md5 = request.form.get('password_md5')
        patient_name = request.form.get('patient_name')

        # Validate user credentials
        # Return error if credentials are invalid
        # Get the uploaded file from the request
        # Check and handle invalid credentials

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        file = request.files.get('file')
        # Check if a file was uploaded
        # Return an error if no file is provided
        # Prepare to save the uploaded file
        # Handle missing file uploads

        if not file:
            return jsonify({'error': 'No file data provided'}), 400

        # Save the uploaded file
        # Get the current epoch timestamp
        # Generate a unique UUID for the filename
        # Create the user's folder path
        # Create the directory if it doesn't exist

        epoch = int(time.time())
        folder_name = str(uuid.uuid4())
        user_folder = os.path.join(DATA_FOLDER, folder_name)
        os.makedirs(user_folder, exist_ok=True)
# Construct the filename using epoch timestamp
# Create the full file path
# Save the uploaded file to the designated path
# Save the uploaded audio file


        file_name = f"{epoch}.wav"
        file_path = os.path.join(user_folder, file_name)
        file.save(file_path)
# Begin audio file analysis
# Call the audio analysis function
# Process the uploaded audio file
# Perform HeartAI inference and spectrogram generation


        # Perform analysis on the file
        inference_result = create_inference_and_spectrogram_file(file_path)

        # Get the relative path of the uploaded file
        # Prepare to store file information in the database
        # Establish a database connection
        # Begin database transaction to update file information

        # Store relative paths
        relative_file_path = os.path.relpath(file_path, DATA_FOLDER)

        with sqlite3.connect(MASTER_DB) as con:
            # Create a database cursor object
            # Execute SQL query to insert analysis data
            # Insert analysis results into the database
            # Add a new entry to the analysis history table

            cur = con.cursor()
            cur.execute(
                "INSERT INTO analysis_history (username, epoch, file_path, inference, patient_name) VALUES (?, ?, ?, ?, ?)",
                (username, epoch, relative_file_path, inference_result, patient_name)
            # Commit changes to the database
            # Return analysis results with HTTP status code 200
            # Send the analysis results to the client
            # Complete the file upload and analysis process

            )
            con.commit()

        return jsonify({'epoch': epoch, 'inference': inference_result}), 200
    # Handle any exceptions during file upload
    # Log the exception details for debugging purposes
    # Return an error message to the client
    # Return error message with HTTP status code 500

    except Exception as e:
        print(f"Error during file upload: {e}")
        return jsonify({'error': 'Failed to process the file'}), 500

# Define a Flask route for accessing analysis history
# Route handles GET requests for history data
# Function to retrieve and return user's analysis history
# Function docstring: API endpoint for accessing analysis history

@app.route('/accesshistory', methods=['GET'])
def access_history():
    try:
        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')
# Validate user credentials
# Return an error response if credentials are invalid
# Check user authentication
# Handle invalid login attempts


        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Establish a connection to the database
        # Create a database cursor object
        # Construct SQL query to fetch analysis history
        # Execute the query to retrieve analysis history

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT id, patient_name, epoch FROM analysis_history WHERE username=? ORDER BY epoch DESC"
            rows = cur.execute(query, (username,)).fetchall()
# Transform query results into desired JSON format
# Return the analysis history data
# Return the formatted data with HTTP status code 200
# Handle any exceptions that occur during processing


        result = [{"id": row[0], "patient_name": row[1], "epoch": row[2]} for row in rows]
        return jsonify(result), 200
    except Exception as e:
        # Log the exception details for debugging
        # Return an error message with HTTP status code 500
        # Define a new route for accessing specific history records
        # This route handles GET requests for individual history entries

        print(f"Error retrieving access history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route('/history/<int:record_id>', methods=['GET'])
# Function to view a specific analysis record
# API endpoint for viewing individual analysis details
# Function to handle requests for specific history entries
# Docstring describing the function's purpose

def view_history(record_id):
    # Begin a try-except block for error handling
    # Retrieve the username from the request parameters
    # Retrieve the password hash from the request parameters
    # Extract authentication details from the request

    try:
        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')

        # Validate user credentials against the database
        # Return an error if credentials are invalid
        # Verify user authorization for the requested record
        # Access control check for the requested record

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if the user is authorized to access the record
        # Establish a database connection
        # Create a database cursor object
        # Construct SQL query to fetch the record details
        # Execute the query to retrieve the specific record

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT patient_name, file_path, inference, doctor_notes, username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()
# Check if a record with the given ID exists
# Extract the username associated with the record
# Retrieve the user's role from the credentials
# Determine if the user has access to the record


        if row:
            record_username = row[4]
            user_role = validate_credentials(username, password_md5)[0]
# Check if the user is authorized to access this record
# Access control check: user must own the record or be a doctor
# Return an error if access is denied
# Handle unauthorized access attempts


            # Allow access if the user owns the record or is a doctor
            if username != record_username and user_role != 'doctor':
                return jsonify({'error': 'Unauthorized access'}), 403
# Return the record details as a JSON response
# Include the patient's name in the response
# Include the relative file path in the response
# Construct the JSON response for the requested record


            return jsonify({
                "patient_name": row[0],
                "file_path": row[1],  # Relative path
                # Include the inference results in the response
                # Include doctor's notes in the response
                # Return the JSON response with HTTP status code 200
                # Handle cases where no matching record is found

                "inference": row[2],
                "doctor_notes": row[3]
            }), 200
        else:
            # Return a "Record not found" error
            # Handle any exceptions that might occur
            # Log the error details for debugging
            # Return a generic error message

            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"Error retrieving history details: {e}")
        return jsonify({'error': 'Failed to retrieve history details'}), 500
# Define a new route for updating doctor's notes
# This route handles POST requests to update notes
# Function to handle updating doctor's notes
# Function docstring: API endpoint to update doctor's notes


@app.route('/update_notes/<int:record_id>', methods=['POST'])
def update_notes(record_id):
    try:
        data = request.get_json()
        # Extract username from the JSON data
        # Extract password hash from the JSON data
        # Extract doctor's notes from the JSON data
        # Retrieve relevant information from the request

        username = data.get('username')
        password_md5 = data.get('password_md5')
        doctor_notes = data.get('doctor_notes')

        # Validate doctor's credentials
        # Return error if credentials are invalid
        # Get the user's role after successful authentication
        # Check if the user is authorized

        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        user_role = validate_credentials(username, password_md5)[0]
        # Check if the user is a doctor
        # Return error if user is not authorized
        # Establish a database connection
        # Begin database transaction to update notes

        if user_role != 'doctor':
            return jsonify({'error': 'Unauthorized: Only doctors can update notes'}), 403

        with sqlite3.connect(MASTER_DB) as con:
            # Create a database cursor object
            # Query to check if the record exists
            # Fetch the username associated with the record ID
            # Verify if the specified record ID exists

            cur = con.cursor()
            # Check if the record exists
            query = "SELECT username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()
# Check if the query returned any rows
# Return a 404 error if the record is not found
# Handle cases where the record does not exist
# Respond with an error if the record ID is invalid


            if not row:
                return jsonify({'error': 'Record not found'}), 404

            # Extract the username from the fetched row
            # Check if the doctor is authorized to update this specific record
            # Implement access control based on record ownership
            # Enforce access control for record modification

            record_username = row[0]

            # Ensure the doctor can only update records they have created
            if username != record_username:
                # Return an error if the doctor is not authorized
                # Handle unauthorized modification attempts
                # Prepare to update the doctor's notes in the database
                # Execute the SQL UPDATE statement

                return jsonify({'error': 'Unauthorized: You can only update your own records'}), 403

            # Update the doctor's notes
            cur.execute(
                # SQL query to update the doctor's notes
                # Parameters for the SQL UPDATE statement
                # Execute the update query
                # Commit changes to the database

                "UPDATE analysis_history SET doctor_notes=? WHERE id=?",
                (doctor_notes, record_id)
            )
            con.commit()
# Return a success message to the client
# Return success status code
# Handle any exceptions during the update process
# Log any errors that occur during the update


        return jsonify({'message': 'Notes updated successfully.'}), 200
    except Exception as e:
        print(f"Error updating notes: {e}")
        # Return an error message if the update fails
        # Return an error status code
        # Define a route for deleting a record
        # Function to handle record deletion requests

        return jsonify({'error': 'Failed to update notes.'}), 500

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    # Function docstring: API endpoint for deleting analysis records
    # Begin a try-except block for error handling
    # Handle potential exceptions during record deletion
    # Try block for deleting a record

    try:
        # Retrieve JSON data from the request
        # Extract username from the JSON data
        # Extract password hash from the JSON data
        # Get user credentials from the request

        data = request.get_json()
        username = data.get('username')
        password_md5 = data.get('password_md5')

        # Validate user credentials
        # Check if credentials are valid
        # Return error if credentials are invalid
        # Handle invalid login attempts

        # Validate user credentials
        role = validate_credentials(username, password_md5)
        if not role:
            return jsonify({'error': 'Invalid credentials'}), 401
# Establish a database connection
# Create a database cursor object
# Query to check record ownership
# Verify record existence and ownership


        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            # Check if the record exists and belongs to the user
            # Execute the query to check record existence and ownership
            # Fetch the username and file path from the database
            # Check if a matching record was found
            # Handle cases where the record does not exist

            cur.execute("SELECT username, file_path FROM analysis_history WHERE id=?", (record_id,))
            row = cur.fetchone()

            if not row:
                # Return an error if the record is not found
                # Handle cases where the record ID is invalid
                # Check if the record belongs to the user
                # Enforce access control based on record ownership

                return jsonify({'error': 'Record not found'}), 404

            record_username, file_path = row
            if record_username != username:
                # Return an error if the user is not authorized to delete the record
                # Handle unauthorized deletion attempts
                # Prepare to delete the record from the database
                # Execute the SQL DELETE statement

                return jsonify({'error': 'Unauthorized: You can only delete your own records'}), 403

            # Delete the record
            cur.execute("DELETE FROM analysis_history WHERE id=?", (record_id,))
            # Commit the changes to the database
            # Prepare to delete the associated files from the file system
            # Construct the absolute path of the file to be deleted
            # Get the full file path for deletion

            con.commit()

            # Optionally delete the files from the file system
            full_file_path = os.path.abspath(os.path.join(DATA_FOLDER, file_path))
            # Check if the file exists before attempting deletion
            # Delete the audio file from the file system
            # Construct the path to the spectrogram image
            # Prepare to delete the associated spectrogram image

            if os.path.exists(full_file_path):
                os.remove(full_file_path)
            # Also remove the spectrogram image
            image_path = full_file_path.replace('.wav', '.png')
            # Check if the spectrogram image exists
            # Delete the spectrogram image from the file system
            # Return a success message to the client
            # Return HTTP status code 200 on successful deletion

            if os.path.exists(image_path):
                os.remove(image_path)

        return jsonify({'message': 'Record deleted successfully.'}), 200
    # Handle any exceptions during record deletion
    # Log the error details for debugging purposes
    # Return an error message to the client
    # Return an error status code

    except Exception as e:
        print(f"Error deleting record: {e}")
        return jsonify({'error': 'Failed to delete record.'}), 500

# Define a route to serve audio files
# Route handles GET requests for audio files
# Function to serve audio files for a given record ID
# Docstring describing the function's purpose

@app.route('/get_audio/<int:record_id>', methods=['GET'])
def get_audio(record_id):
    try:
        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')
# Validate user credentials
# Return error if credentials are invalid
# Check user authentication
# Handle invalid login attempts


        if not validate_credentials(username, password_md5):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Establish a database connection
        # Create a database cursor object
        # Construct SQL query to fetch file path and username
        # Execute the query to retrieve the file path and username

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            query = "SELECT file_path, username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()
# Check if a record with the given ID exists
# Extract file path and record username from the result
# Get the user's role after successful authentication
# Determine if the user has access to the record


        if row:
            file_path, record_username = row
            user_role = validate_credentials(username, password_md5)[0]
# Check if the user is authorized to access this record
# Access control: user must own the record or be a doctor
# Return an error if access is denied
# Handle unauthorized access attempts


            if username != record_username and user_role != 'doctor':
                return jsonify({'error': 'Unauthorized access'}), 403

            # Construct the absolute path to the audio file
            # Check if the audio file exists
            # Create a Flask response to send the audio file
            # Set CORS headers to allow access from any origin

            full_file_path = os.path.abspath(os.path.join(DATA_FOLDER, file_path))
            if os.path.exists(full_file_path):
                response = make_response(send_file(full_file_path, mimetype='audio/wav'))
                response.headers['Access-Control-Allow-Origin'] = '*'
                # Return the response containing the audio file
                # Handle cases where the audio file is not found
                # Log a message indicating the file not found
                # Return an error response if the file is missing

                return response
            else:
                print(f"Audio file not found at: {full_file_path}")
                return jsonify({'error': 'File not found'}), 404
        # Return an error if the record is not found
        # Handle cases where the record ID is invalid
        # Log any exceptions that occur during audio file serving
        # Handle any unexpected errors during file serving

        else:
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"Error serving audio file: {e}")
        # Return an error response with HTTP status code 500
        # Handle any unexpected errors during audio file serving
        # Define a route to serve spectrogram images
        # Function to handle requests for spectrogram images

        return jsonify({'error': 'Failed to serve audio file.'}), 500

@app.route('/get_image/<int:record_id>', methods=['GET'])
def get_image(record_id):
    # Function docstring describing its purpose
    # Begin a try-except block for error handling
    # Handle potential exceptions during image serving
    # Try block for serving the spectrogram image

    try:
        # Retrieve username from the request parameters
        # Retrieve password hash from the request parameters
        # Validate user credentials
        # Check if the provided credentials are valid

        username = request.args.get('username')
        password_md5 = request.args.get('password_md5')

        if not validate_credentials(username, password_md5):
            # Return an error response if credentials are invalid
            # Handle invalid login attempts
            # Establish a database connection
            # Create a database cursor object

            return jsonify({'error': 'Invalid credentials'}), 401

        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            # Construct SQL query to fetch file path and username
            # Execute the query to retrieve the file path and username
            # Check if a record with the given ID exists
            # Handle cases where the record is not found

            query = "SELECT file_path, username FROM analysis_history WHERE id=?"
            row = cur.execute(query, (record_id,)).fetchone()

        if row:
            # Extract file path and record username from the fetched row
            # Retrieve the user's role from the credentials
            # Check if the user is authorized to access this record
            # Enforce access control based on record ownership and user role

            file_path, record_username = row
            user_role = validate_credentials(username, password_md5)[0]

            if username != record_username and user_role != 'doctor':
                # Return an error if the user is not authorized
                # Handle unauthorized access attempts
                # Construct the path to the spectrogram image
                # Create the image file path

                return jsonify({'error': 'Unauthorized access'}), 403

            # Replace .wav with .png to get the image path
            image_relative_path = file_path.replace('.wav', '.png')
            # Construct the full path to the spectrogram image
            # Check if the image file exists
            # Create a Flask response to send the image file
            # Set CORS headers to allow access from any origin

            full_image_path = os.path.abspath(os.path.join(DATA_FOLDER, image_relative_path))
            if os.path.exists(full_image_path):
                response = make_response(send_file(full_image_path, mimetype='image/png'))
                response.headers['Access-Control-Allow-Origin'] = '*'
                # Return the response containing the image file
                # Handle cases where the image file is not found
                # Log a message indicating the file not found
                # Return an error response if the image is missing

                return response
            else:
                print(f"Image file not found at: {full_image_path}")
                return jsonify({'error': 'Image not found'}), 404
        # Return an error if the record is not found
        # Handle cases where the record ID is invalid
        # Log any exceptions that occur during image file serving
        # Handle any unexpected errors during file serving

        else:
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"Error serving image file: {e}")
        # Return an error response with HTTP status code 500
        # Handle any unexpected errors during image file serving
        # Check if the database file exists
        # Handle the case where the database file is missing

        return jsonify({'error': 'Failed to serve image file.'}), 500

if __name__ == '__main__':
    if not os.path.exists(MASTER_DB):
        # Handle database initialization
        # Establish database connection
        # Create database cursor
        # Execute SQL statement to create tables

        # Initialize the database if it doesn't exist
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            cur.execute(
                # SQL statement to create the credentials table
                # Define table schema for user credentials
                # Specify table columns and constraints
                # Create credentials table

                """CREATE TABLE credentials (
                    username TEXT PRIMARY KEY,
                    password_md5 TEXT NOT NULL,
                    folder_name TEXT NOT NULL,
                    role TEXT NOT NULL
                )"""
            )
            cur.execute(
                # SQL statement to create the analysis_history table
                # Define table schema for analysis history
                # Specify table columns and constraints
                # Create analysis_history table

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
    # Handle existing database case
    # Check for the 'doctor_notes' column
    # Establish database connection
    # Create database cursor

    else:
        # Check if 'doctor_notes' column exists; if not, add it
        with sqlite3.connect(MASTER_DB) as con:
            cur = con.cursor()
            # Query table schema to check for column existence
            # Retrieve column names from the table
            # Check if doctor_notes column exists
            # Add doctor_notes column if it doesn't exist

            cur.execute("PRAGMA table_info(analysis_history)")
            columns = [info[1] for info in cur.fetchall()]
            if 'doctor_notes' not in columns:
                cur.execute("ALTER TABLE analysis_history ADD COLUMN doctor_notes TEXT")
                con.commit()
    app.run(host='0.0.0.0', port=8080)
