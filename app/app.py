import base64
import logging
import os
from datetime import datetime

import schedule

from service.naukri import Naukri
from utils.encryption import decrypt_password
from utils.utils import load_users_data, write_response_in_file


def job():
    try:
        naukri = Naukri()

        # Load users data
        users_data = load_users_data()
        logging.info(f"users data: {users_data}")
        for username, details in users_data.items():
            encoded_password = details.get("password")
            encrypted_password = base64.b64decode(encoded_password)
            password = decrypt_password(encrypted_password)
            mobile_number = details.get("number")
            resume_path = details.get("resume")
            output = naukri.run(username, password, mobile_number, resume_path)
            date_time = datetime.now()
            if output is True:
                write_response_in_file(
                    f"{username} Profile Updated successfully on {date_time}"
                )
            else:
                write_response_in_file(
                    f"{username} Profile Updated failed. RunTime: {date_time}"
                )
    except Exception as err:
        logging.error(f"Job Failed, Error: {err}")
        return False


def scheduling():
    # Initial scheduling of the main job
    execution_slots_str = os.getenv("execution_time_slots", ["09:30", "14:00", "18:00"])
    execution_time_slots = (
        eval(execution_slots_str)
        if type(execution_slots_str) == str
        else execution_slots_str
    )
    for execution_time in execution_time_slots:
        schedule.every().day.at(str(execution_time)).do(job)


def run():
    scheduling()
    schedule.run_pending()
    # while True:
    #     logging.info(f"Checking job scheduler: Time: {datetime.now()}")
    #     schedule.run_pending()
    #     time.sleep(10 * 30)
