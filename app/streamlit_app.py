import streamlit as st
import os
from utils.utils import load_users_data, update_users_data
from app import run
from utils.encryption import encrypt_password
import base64

st.header("Naukri Resume Auto Updater", divider="grey")

user_name = st.text_input("Naukri UserName")
password = st.text_input("Password", type="password")
mobile_number = st.text_input("Enter your mobile number:", max_chars=10)

resume = st.file_uploader("Upload Resume", type=["pdf"], accept_multiple_files=False)


# Mobile Number validation
def check_input_validation():
    if mobile_number:
        if len(mobile_number) == 10 and mobile_number.isdigit():
            st.empty()
            return True
        else:
            st.error("Mobile number must be 10 digits and contain only numbers.")
            return False


is_valid = check_input_validation()

submit_button = st.button(label="Submit", disabled=not is_valid)

load_data = st.button(label="Load users data")

clear_button = st.button("Clear")
if load_data:
    load_users_data = load_users_data()
    st.json(load_users_data)
if clear_button:
    st.empty()

# Submit button handler
if submit_button:
    # Upload resume
    if resume is not None:
        # Save the resume file
        output_dir = "data/resumes"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, resume.name)

        with open(output_path, "wb") as f:
            f.write(resume.getbuffer())

        # Load users data
        users_data = load_users_data()

        # Encode the encrypted password as a Base64 string
        encrypt_password = encrypt_password(password)
        encoded_password = base64.b64encode(encrypt_password).decode()

        # Update users data
        user = {
            "name": user_name,
            "password": encoded_password,
            "number": mobile_number,
            "resume": output_path,
        }
        users_data[user_name] = user

        # Save updated users data
        message, status = update_users_data(users_data)
        if status:
            st.success(message)
            run()
        else:
            st.error(message)
    else:
        st.error("Please upload your resume.")
