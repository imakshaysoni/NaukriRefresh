import os
import json

users_file_path = "data/users_data.json"


def load_users_data():
    # Load users data
    if os.path.exists(users_file_path):
        with open(users_file_path, "r") as file:
            try:
                users_data = json.load(file)
            except json.JSONDecodeError:
                users_data = {}
    else:
        users_data = {}
    return users_data


def update_users_data(users_data):
    try:
        print(users_data)
        with open(users_file_path, "w") as file:
            json.dump(users_data, file, indent=4)
            return (
                "Request Received, We will update your resume on naukri once a day."
                "Best of luck for you job hunting.",
                True,
            )
    except Exception as e:
        return (
            f"An error occurred while updating your details to our server, Please try again or contact us on mail"
            f"Developer Error: : {e}",
            False,
        )


def write_response_in_file(content):
    response_file_path = "app/response/response.txt"
    with open(response_file_path, "a") as file:
        file.write(f"\n{content}")
