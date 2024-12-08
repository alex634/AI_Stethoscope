# Import necessary libraries for the Streamlit web app.
# Import the requests library for making HTTP requests.
# Import the hashlib library for cryptographic hashing.
# Import the datetime library for working with dates and times.

import streamlit as st
import requests
import hashlib
import datetime
# Define the backend URL for the application.
# Define a function to hash passwords for security.
# This function will take a password as input.
# It will then return the hashed password.


BACKEND_URL = "http://127.0.0.1:8080"

def hash_password(password):
    # Hash the password using MD5 and return the hexadecimal digest.
    # Define a dictionary to store inference messages.
    # "normal" key stores the message for normal heartbeats.
    # This dictionary will be used to provide user-friendly feedback.

    return hashlib.md5(password.encode()).hexdigest()

INFERENCE_MESSAGES = {
    "normal": "No abnormality was found in the heartbeat.",
    "abnormal": "An abnormality was detected in the heartbeat.",
    "present": "No abnormality was found in the heartbeat.",  

}
# Define the main function for the Streamlit application.
# Check if the user is logged in using Streamlit's session state.
# If the "logged_in" key is not in the session state,
# Initialize the "logged_in" key to False.


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Check if the "page" key exists in the session state.
    # If not, set the default page to "login".
    # Check if the "refresh" key exists in the session state.
    # If not, set the default refresh state to False.

    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "refresh" not in st.session_state:
        st.session_state.refresh = False
# Check if the user is logged in.
# If logged in, run the main application.
# Otherwise, check if the current page is the login page.
# If it is the login page, proceed with login logic.


    if st.session_state.logged_in:
        main_app()
    elif st.session_state.page == "login":
        # If the current page is the login page, run the login_page function.
        # Otherwise, check if the current page is the register page.
        # If it is the register page, run the register_page function.
        # This section handles routing to different pages based on session state.

        login_page()
    elif st.session_state.page == "register":
        register_page()

# Define a function to display the login page.
# Set the title of the page to "Login".
# Check if the "login_role" key exists in the session state.
# Initialize "login_role" if it doesn't exist to handle first-time access.

def login_page():
    st.title("Login")

    if "login_role" not in st.session_state:
        # If not, set the default login role to "Doctor".
        # Create a radio button to select the user role ("Doctor" or "Patient").
        # Use the key "login_role" to manage the selection in session state.
        # Get the username from the user using a text input and store it with key "login_username".

        st.session_state.login_role = "Doctor"
    role = st.radio("Select your role", ["Doctor", "Patient"], key="login_role")

    username = st.text_input("Username", key="login_username")
    # Get the password from the user using a text input with password masking.
    # Use the key "login_password" to store the password in session state.
    # Create a button labeled "Log In" to trigger the login process.
    # Check if the username or password fields are empty.

    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In"):
        if not username or not password:
            # If either field is empty, display an error message.
            # Otherwise, hash the entered password using the hash_password function.
            # Make a POST request to the backend server to authenticate the user.
            # The request will include the username and hashed password.

            st.error("Please enter both username and password.")
        else:
            hashed_password = hash_password(password)
            response = requests.post(
                # Construct the URL for the login endpoint using the BACKEND_URL.
                # Send a JSON payload containing the username and hashed password.
                # The payload is sent to the backend for authentication.
                # This sends the login request to the specified backend URL.

                f"{BACKEND_URL}/login",
                json={"username": username, "password_md5": hashed_password}
            )

            # Check if the login request was successful (status code 200).
            # Parse the JSON response from the server.
            # Verify that the returned role matches the selected role.
            # If successful, update the session state to indicate that the user is logged in.

            if response.status_code == 200:
                data = response.json()
                if data["role"] == role.lower():
                    st.session_state.logged_in = True
                    # Store the username in the session state.
                    # Store the hashed password in the session state.
                    # Store the user's role in the session state.
                    # Redirect to the main application page.

                    st.session_state.username = username
                    st.session_state.password_md5 = hashed_password
                    st.session_state.role = role
                    st.session_state.page = "main_app"  
                    # Display a success message if login was successful.
                    # Otherwise, display an error message indicating a role mismatch.
                    # Handle cases where the login request failed (non-200 status code).
                    # This section manages feedback to the user after the login attempt.

                    st.success("Login successful!")
                else:
                    st.error("Role mismatch. Please check your selected role.")
            else:
                # Display an error message if the username or password is incorrect.
                # Create a button to navigate to the registration page.
                # Clicking this button changes the session state to redirect.
                # This section handles unsuccessful login attempts and registration redirection.

                st.error("Invalid username or password.")

    if st.button("Go to Register"):
        st.session_state.page = "register"
# Define a function to handle the registration page.
# Set the title of the page to "Register".
# This function will contain the registration form elements.
# This function manages the user registration process.


def register_page():
    st.title("Register")

    # Check if the "register_role" key exists in the session state.
    # If not, set the default registration role to "Doctor".
    # Provide a radio button to select the user's role ("Doctor" or "Patient").
    # Use the key "register_role" to manage the role selection in the session state.

    if "register_role" not in st.session_state:
        st.session_state.register_role = "Doctor"
    role = st.radio("Select your role", ["Doctor", "Patient"], key="register_role")

    # Get the username from the user using a text input.
    # Get the password from the user using a password input field.
    # Create a button to trigger the registration process.
    # This section gathers user input for registration.

    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")

    if st.button("Register"):
        # Check if the username field is empty.
        # If empty, display an error message prompting the user to enter a username.
        # Check if the password field is empty.
        # If empty, display an error message prompting the user to enter a password.

        if not username:
            st.error("Please enter a username.")
        elif not password:
            st.error("Please enter a password.")
        # Check if the password is less than 6 characters long.
        # If so, display an error message specifying the minimum length requirement.
        # Otherwise, proceed to hash the password.
        # This section validates the password length before hashing.

        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            hashed_password = hash_password(password)
            # Make a POST request to the backend's user creation endpoint.
            # Send the username, hashed password, and role in the JSON payload.
            # This request attempts to create a new user account on the backend.
            # The backend will handle user creation and data persistence.

            response = requests.post(
                f"{BACKEND_URL}/createuser",
                json={"username": username, "password_md5": hashed_password, "role": role.lower()}
            )
# Check if the registration request was successful (status code 200).
# If successful, display a success message and redirect to the login page.
# Update the session state to reflect the page change.
# This section handles successful registration and redirects the user.


            if response.status_code == 200:
                st.success("Registration successful! Please log in.")
                st.session_state.page = "login"
            # Handle the case where the username already exists (status code 400).
            # Display an appropriate error message to the user.
            # Handle other registration errors (non-200 and non-400 status codes).
            # Provide a generic error message for unexpected issues.

            elif response.status_code == 400:
                st.error("Username already exists.")
            else:
                st.error("Failed to register. Please try again.")
# Add a button to allow users to return to the login page.
# Clicking this button changes the session state.
# This facilitates navigation back to the login screen.
# This provides a user-friendly way to switch between registration and login.


    if st.button("Back to Login"):
        st.session_state.page = "login"

# Define the main application function.
# Display a welcome message using the username and role from the session state.
# Create two tabs for the main application: "Upload and Analyze" and "View History".
# This function will contain the core functionality of the application.

def main_app():
    st.title(f"Welcome, {st.session_state['username']} ({st.session_state['role']})!")

    tab1, tab2 = st.tabs(["Upload and Analyze", "View History"])
# Begin the "Upload and Analyze" tab content.
# Display a subheader indicating the tab's purpose.
# Check if the currently logged-in user is a patient.
# This section handles the content specific to the patient role.


    with tab1:
        st.subheader("Upload and Analyze")
        if st.session_state.role == 'Patient':
# Retrieve the patient's name from the session state.
# Display the patient's name on the page.
# Handle the case where the user is not a patient.
# This section displays patient-specific information.


            patient_name = st.session_state.username
            st.write(f"Patient Name: {patient_name}")
        else:
# If the user is not a patient, allow them to input a patient name.
# Provide a file uploader for heartbeat audio files (WAV or FLAC).
# This section handles file uploads for analysis.
# The uploaded file will be used for subsequent processing.


            patient_name = st.text_input("Patient Name")
        uploaded_file = st.file_uploader("Upload heartbeat audio file (WAV/FLAC)", type=["wav", "flac"])

        # Create a button to initiate the analysis process.
        # Check if both a file and patient name have been provided.
        # Prepare the file for sending to the backend.
        # This section handles the analysis request initiation.

        if st.button("Analyze"):
            if uploaded_file and patient_name:
                files = {"file": (uploaded_file.name, uploaded_file.read())}
                data = {
                    # Include the username from the session state in the request data.
                    # Include the hashed password from the session state.
                    # Include the patient's name in the request data.
                    # This section constructs the data payload for the backend request.

                    "username": st.session_state.username,
                    "password_md5": st.session_state.password_md5,
                    "patient_name": patient_name
                }
                # Send a POST request to the backend's upload endpoint.
                # Include both the file and the data payload in the request.
                # Check if the upload was successful (status code 200).
                # Parse the JSON response containing the analysis result.

                response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
# Retrieve the inference message from the INFERENCE_MESSAGES dictionary.
# Use the inference result from the response as the key.
# Provide a default message if the inference result is not found in the dictionary.
# This ensures a user-friendly message is always displayed.


                    inference_message = INFERENCE_MESSAGES.get(
                        result["inference"].lower(),
                        f"Inference result: {result['inference']}"
                    # Close the get method and assign it to inference_message.
                    # Indicate successful analysis to the user.
                    # Display the inference result to the user.
                    # Handle cases where the analysis request failed.

                    )
                    st.success("Analysis complete!")
                    st.write("Inference Result:", inference_message)
                else:
                    # Display an error message if the file processing failed.
                    # Handle cases where neither file nor patient name was provided.
                    # Provide informative error messages to guide the user.
                    # This section manages error handling and user feedback.

                    st.error("Failed to process file.")
            else:
                st.error("Please provide patient name and file.")

    # Start a new section for the "View History" tab.
    # Display a subheader to indicate the tab's purpose.
    # Check the user's role to determine whether to display history data.
    # This section controls the display of historical data based on user role.

    with tab2:
        st.subheader("View History")

        if st.session_state.role == "Doctor":
            # Create two columns for layout using st.columns.
            # The first column will contain a selectbox for sorting options.
            # The selectbox allows the doctor to choose between sorting by date or patient name.
            # This section sets up the user interface for sorting historical data.

            col1, col2 = st.columns([1, 2])
            with col1:
                sort_option = st.selectbox("Sort by", ["Date", "Patient Name"])
            with col2:
                # Create a text input for searching by patient name.
                # This allows doctors to search for specific patient records.
                # This input field will be used to filter the displayed history.
                # If the user is not a doctor, set a default sort option.

                search_query = st.text_input("Search by Patient Name")
        else:

            sort_option = "Date"
            # Set a default empty search query if no search term is provided.
            # Make a GET request to the backend to retrieve the history.
            # The request will be sent to the backend's history access endpoint.  
            # This retrieves historical data from the backend server.

            search_query = ""

        response = requests.get(
            f"{BACKEND_URL}/accesshistory",
            # Include authentication details in the request parameters.
            # Send the username and hashed password for authentication.
            # This ensures only authorized users can access the history.
            # Check if the request to access history was successful.

            params={"username": st.session_state.username, "password_md5": st.session_state.password_md5}
        )

        if response.status_code == 200:
            # Parse the JSON response containing the history data.
            # If the user is a doctor and a search query is provided, filter the results.
            # Filter the history to include only records matching the search query.
            # This section filters and prepares the history data for display.

            history = response.json()

            if st.session_state.role == "Doctor" and search_query:
                history = [record for record in history if search_query.lower() in record['patient_name'].lower()]
# Check if the selected sort option is "Date".
# If so, sort the history by the 'epoch' field in descending order.
# Handle the case where the sort option is "Patient Name".
# This section sorts the history data according to the user's selection.


            if sort_option == "Date":
                history.sort(key=lambda x: x['epoch'], reverse=True)
            elif sort_option == "Patient Name":
                # Sort the history by patient name in ascending order.
                # Iterate through each record in the sorted history.
                # Convert the epoch timestamp to a human-readable date and time format.
                # This section formats the data for display to the user.

                history.sort(key=lambda x: x['patient_name'])

            for record in history:
                display_date = datetime.datetime.fromtimestamp(record['epoch']).strftime('%Y-%m-%d %H:%M:%S')
                # Create an expander for each record in the history.
                # The expander title will display the patient name and date.
                # Make a GET request to the backend to retrieve detailed information.
                # This request retrieves details for a specific record ID.

                with st.expander(f"{record['patient_name']} - {display_date}"):

                    details_response = requests.get(
                        f"{BACKEND_URL}/history/{record['id']}",
                        # Include authentication parameters in the details request.
                        # Send the username and hashed password for authorization.
                        # This ensures only authorized users can access detailed history.
                        # This section adds security to the request for detailed information.

                        params={
                            "username": st.session_state.username,
                            "password_md5": st.session_state.password_md5
                        }
                    # Close the request to get detailed information.
                    # Check if the request for details was successful.
                    # Parse the JSON response containing the detailed data.
                    # This section handles the response from the detailed information request.

                    )
                    if details_response.status_code == 200:
                        details_data = details_response.json()

                        # Retrieve the inference message from the INFERENCE_MESSAGES dictionary.
                        # Use the inference result from the detailed data as the key.
                        # Provide a default message if the inference result is not found.
                        # This ensures a user-friendly message is always displayed for the details.

                        inference_message = INFERENCE_MESSAGES.get(
                            details_data["inference"].lower(),
                            f"Inference result: {details_data['inference']}"
                        )
                        # Display the patient's name from the detailed data.
                        # Display the inference message for the specific record.
                        # Construct the URL to access the audio file for this record.
                        # This URL includes authentication parameters for secure access.

                        st.write("Patient Name:", details_data["patient_name"])
                        st.write("Inference:", inference_message)

                        audio_url = f"{BACKEND_URL}/get_audio/{record['id']}?username={st.session_state.username}&password_md5={st.session_state.password_md5}"
                        # Construct the URL to access the image file for this record, including authentication.
                        # Display the audio file using st.audio.
                        # Display the image file using st.image.
                        # This section displays the audio and image associated with the record.

                        image_url = f"{BACKEND_URL}/get_image/{record['id']}?username={st.session_state.username}&password_md5={st.session_state.password_md5}"

                        st.audio(audio_url)
                        st.image(image_url)
# Check if the current user is a doctor.
# If so, display a text area for doctor's notes.
# The text area allows doctors to add or edit notes for the record.
# This section provides a space for doctors to add their observations.


                        if st.session_state.role == "Doctor":
                            doctor_notes = st.text_area(
                                "Doctor's Notes",
                                # Populate the text area with existing doctor's notes, if any.
                                # Use a unique key for each record to manage notes independently.
                                # Create a button to save the doctor's notes.
                                # The button's key ensures unique functionality for each record.

                                value=details_data.get("doctor_notes", ""),
                                key=f"notes_{record['id']}"
                            )
                            if st.button("Save Notes", key=f"save_notes_{record['id']}"):
# Make a POST request to update the doctor's notes on the backend.
# The request targets a specific record ID for updating.
# Prepare the JSON payload for the update request.
# This section sends the updated notes to the backend for persistence.


                                update_response = requests.post(
                                    f"{BACKEND_URL}/update_notes/{record['id']}",
                                    json={
                                        # Include authentication details in the update request.
                                        # Send the username and hashed password for security.
                                        # Include the updated doctor's notes in the payload.
                                        # This ensures only authorized users can modify notes and maintains data integrity.

                                        "username": st.session_state.username,
                                        "password_md5": st.session_state.password_md5,
                                        "doctor_notes": doctor_notes
                                    }
                                # Close the JSON payload and send the update request.
                                # Check if the update request was successful.
                                # Display a success message if the notes were saved.
                                # Handle cases where the notes update failed.

                                )
                                if update_response.status_code == 200:
                                    st.success("Notes saved successfully.")
                                else:
                                    # Extract a specific error message from the response, or use a default.
                                    # Display the error message to the user.
                                    # Handle the case where the user is not a doctor.
                                    # This section displays error messages and handles cases where the user is not a doctor.

                                    error_message = update_response.json().get('error', 'Failed to save notes.')
                                    st.error(f"Error: {error_message}")
                        else:

                            # Retrieve the doctor's notes from the details data, using an empty string as a default.
                            # Check if doctor's notes exist for the current record.
                            # If notes exist, display a label and the notes themselves.
                            # This section displays existing doctor's notes if available.

                            doctor_notes = details_data.get("doctor_notes", "")
                            if doctor_notes:
                                st.write("Doctor's Notes:")
                                st.write(doctor_notes)
                            # If no doctor's notes are found, display a message indicating this.
                            # Add a button to delete the current record.
                            # The button key ensures uniqueness for each record's delete operation.
                            # This section handles the display of a "no notes" message and provides a delete functionality.

                            else:
                                st.write("No doctor's notes available.")

                        if st.button("Delete Record", key=f"delete_{record['id']}"):
                            # Send a POST request to the backend to delete the specified record.
                            # The URL includes the record ID to target the correct entry.
                            # Include authentication details (username and password) in the request.
                            # This ensures only authorized users can perform deletion actions.

                            delete_response = requests.post(
                                f"{BACKEND_URL}/delete_record/{record['id']}",
                                json={
                                    "username": st.session_state.username,
                                    # Include the hashed password for authentication in the JSON payload.
                                    # Close the JSON payload and send the delete request.
                                    # Check if the deletion was successful (status code 200).
                                    # This section completes the request and checks for successful deletion.

                                    "password_md5": st.session_state.password_md5
                                }
                            )
                            if delete_response.status_code == 200:
                                # Display a success message to the user.
                                # Update the session state to trigger a refresh.
                                # This refresh will update the displayed history.
                                # Handle cases where record deletion failed.

                                st.success("Record deleted successfully.")

                                st.session_state.refresh = not st.session_state.refresh
                            else:
                                # Extract an error message from the response or use a default message.
                                # Display the error message to inform the user about the failure.
                                # Handle cases where loading the details failed (non-200 status code).
                                # This section provides error handling and user feedback for failed requests.

                                error_message = delete_response.json().get('error', 'Failed to delete record.')
                                st.error(f"Error: {error_message}")
                    else:
                        st.error("Failed to load details.")
# Handle cases where the history could not be loaded.
# Display a generic error message to the user.
# This section provides error handling for history retrieval failures.
# This ensures user is informed of any issues loading historical data.


        else:
            st.error("Failed to load history.")

    # Add a button to allow users to log out.
    # Upon clicking, set the logged_in status to False.
    # Redirect the user to the login page after logout.
    # This section manages the logout process and redirects to login.

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

if __name__ == "__main__":
    main()
