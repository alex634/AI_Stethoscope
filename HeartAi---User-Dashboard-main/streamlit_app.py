import streamlit as st
import requests
import hashlib
import datetime

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8080"

# Helper function to hash passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Mapping for inference results to user-friendly messages
INFERENCE_MESSAGES = {
    "normal": "No abnormality was found in the heartbeat.",
    "abnormal": "An abnormality was detected in the heartbeat.",
    "present": "No abnormality was found in the heartbeat.",  # Assuming 'present' means normal
    # Add more mappings if necessary
}

# Navigation and Main Logic
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "refresh" not in st.session_state:
        st.session_state.refresh = False

    if st.session_state.logged_in:
        main_app()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()

# Login Page
def login_page():
    st.title("Login")

    if "login_role" not in st.session_state:
        st.session_state.login_role = "Doctor"
    role = st.radio("Select your role", ["Doctor", "Patient"], key="login_role")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In"):
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            hashed_password = hash_password(password)
            response = requests.post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password_md5": hashed_password}
            )

            if response.status_code == 200:
                data = response.json()
                if data["role"] == role.lower():
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.password_md5 = hashed_password
                    st.session_state.role = role
                    st.session_state.page = "main_app"  # Navigate to main app
                    st.success("Login successful!")
                else:
                    st.error("Role mismatch. Please check your selected role.")
            else:
                st.error("Invalid username or password.")

    if st.button("Go to Register"):
        st.session_state.page = "register"
        # No need to force rerun; Streamlit will rerun on state change

# Registration Page
def register_page():
    st.title("Register")

    if "register_role" not in st.session_state:
        st.session_state.register_role = "Doctor"
    role = st.radio("Select your role", ["Doctor", "Patient"], key="register_role")

    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")

    if st.button("Register"):
        if not username:
            st.error("Please enter a username.")
        elif not password:
            st.error("Please enter a password.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            hashed_password = hash_password(password)
            response = requests.post(
                f"{BACKEND_URL}/createuser",
                json={"username": username, "password_md5": hashed_password, "role": role.lower()}
            )

            if response.status_code == 200:
                st.success("Registration successful! Please log in.")
                st.session_state.page = "login"
            elif response.status_code == 400:
                st.error("Username already exists.")
            else:
                st.error("Failed to register. Please try again.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        # No need to force rerun; Streamlit will rerun on state change

# Main Application (After Login)
def main_app():
    st.title(f"Welcome, {st.session_state['username']} ({st.session_state['role']})!")

    tab1, tab2 = st.tabs(["Upload and Analyze", "View History"])

    # Upload Tab
    with tab1:
        st.subheader("Upload and Analyze")
        if st.session_state.role == 'Patient':
            # Patients cannot change patient name; it's their own username
            patient_name = st.session_state.username
            st.write(f"Patient Name: {patient_name}")
        else:
            # Doctors can input patient names
            patient_name = st.text_input("Patient Name")
        uploaded_file = st.file_uploader("Upload heartbeat audio file (WAV/FLAC)", type=["wav", "flac"])

        if st.button("Analyze"):
            if uploaded_file and patient_name:
                files = {"file": (uploaded_file.name, uploaded_file.read())}
                data = {
                    "username": st.session_state.username,
                    "password_md5": st.session_state.password_md5,
                    "patient_name": patient_name
                }
                response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
                    # Map the inference result to a user-friendly message
                    inference_message = INFERENCE_MESSAGES.get(
                        result["inference"].lower(),
                        f"Inference result: {result['inference']}"
                    )
                    st.success("Analysis complete!")
                    st.write("Inference Result:", inference_message)
                else:
                    st.error("Failed to process file.")
            else:
                st.error("Please provide patient name and file.")

    # History Tab
    with tab2:
        st.subheader("View History")

        # Sorting options and search bar for Doctors
        if st.session_state.role == "Doctor":
            col1, col2 = st.columns([1, 2])
            with col1:
                sort_option = st.selectbox("Sort by", ["Date", "Patient Name"])
            with col2:
                search_query = st.text_input("Search by Patient Name")
        else:
            # For patients, only sorting by date is available
            sort_option = "Date"
            search_query = ""

        # Fetch history
        response = requests.get(
            f"{BACKEND_URL}/accesshistory",
            params={"username": st.session_state.username, "password_md5": st.session_state.password_md5}
        )

        if response.status_code == 200:
            history = response.json()

            # Filter history based on search query (only for doctors)
            if st.session_state.role == "Doctor" and search_query:
                history = [record for record in history if search_query.lower() in record['patient_name'].lower()]

            # Sort history
            if sort_option == "Date":
                history.sort(key=lambda x: x['epoch'], reverse=True)
            elif sort_option == "Patient Name":
                history.sort(key=lambda x: x['patient_name'])

            # Display history records
            for record in history:
                display_date = datetime.datetime.fromtimestamp(record['epoch']).strftime('%Y-%m-%d %H:%M:%S')
                # Removed the 'key' argument from st.expander()
                with st.expander(f"{record['patient_name']} - {display_date}"):
                    # Fetch detailed information for the record
                    details_response = requests.get(
                        f"{BACKEND_URL}/history/{record['id']}",
                        params={
                            "username": st.session_state.username,
                            "password_md5": st.session_state.password_md5
                        }
                    )
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        # Map the inference result to a user-friendly message
                        inference_message = INFERENCE_MESSAGES.get(
                            details_data["inference"].lower(),
                            f"Inference result: {details_data['inference']}"
                        )
                        st.write("Patient Name:", details_data["patient_name"])
                        st.write("Inference:", inference_message)
                        st.audio(details_data["file_path"])
                        st.image(details_data["file_path"].replace(".wav", ".png"))

                        # Display and edit doctor notes if the user is a doctor
                        if st.session_state.role == "Doctor":
                            doctor_notes = st.text_area(
                                "Doctor's Notes",
                                value=details_data.get("doctor_notes", ""),
                                key=f"notes_{record['id']}"
                            )
                            if st.button("Save Notes", key=f"save_notes_{record['id']}"):
                                # Send updated notes to the backend
                                update_response = requests.post(
                                    f"{BACKEND_URL}/update_notes/{record['id']}",
                                    json={
                                        "username": st.session_state.username,
                                        "password_md5": st.session_state.password_md5,
                                        "doctor_notes": doctor_notes
                                    }
                                )
                                if update_response.status_code == 200:
                                    st.success("Notes saved successfully.")
                                else:
                                    error_message = update_response.json().get('error', 'Failed to save notes.')
                                    st.error(f"Error: {error_message}")
                        else:
                            # For patients, display the doctor's notes if available
                            doctor_notes = details_data.get("doctor_notes", "")
                            if doctor_notes:
                                st.write("Doctor's Notes:")
                                st.write(doctor_notes)
                            else:
                                st.write("No doctor's notes available.")

                        # Add a delete button
                        if st.button("Delete Record", key=f"delete_{record['id']}"):
                            delete_response = requests.post(
                                f"{BACKEND_URL}/delete_record/{record['id']}",
                                json={
                                    "username": st.session_state.username,
                                    "password_md5": st.session_state.password_md5
                                }
                            )
                            if delete_response.status_code == 200:
                                st.success("Record deleted successfully.")
                                # Trigger a rerun by updating a session state variable
                                st.session_state.refresh = not st.session_state.refresh
                            else:
                                error_message = delete_response.json().get('error', 'Failed to delete record.')
                                st.error(f"Error: {error_message}")
                    else:
                        st.error("Failed to load details.")

        else:
            st.error("Failed to load history.")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        # No need to force rerun; Streamlit will rerun on state change

# Run the application
if __name__ == "__main__":
    main()
