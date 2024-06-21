#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""

import schedule
import io
import logging
import os
import sys
import time
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits
from dotenv import load_dotenv
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM
import pickle
from webdriver_manager.chrome import ChromeDriverManager

# Load Envs
load_dotenv()
# Add folder Path of your resume
originalResumePath = os.getenv("resume_path")

# Add Path where modified resume should be saved
modifiedResumePath = os.getenv("resume_path")

# Update your naukri username and password here before running
username = os.getenv("email_address")
password = os.getenv("password")
mob = os.getenv("mobile_number")  # Type your mobile number here

# False if you don't want to add Random HIDDEN chars to your resume
updatePDF = False

# ----- No other changes required -----

# Set login URL
NaukriURL = "https://www.naukri.com/nlogin/login"

logging.basicConfig(
    level=logging.ERROR, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ["WDM_LOCAL"] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"

# Retry Time
retry_time = int(os.getenv("retry_time", 10))  # in Minutes
# headless
headless_mode = os.getenv("headless", False)


# # Function to save session data
# def save_session(driver, filename):
#     with open(filename, 'wb') as f:
#         pickle.dump(driver.get_cookies(), f)
#
# # Function to load session data
# def load_session(driver, filename):
#     with open(filename, 'rb') as f:
#         cookies = pickle.load(f)
#         for cookie in cookies:
#             driver.add_cookie(cookie)


def log_msg(message):
    """Print to console and store to Log"""
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    _, _, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    logging.error(msg)
    log_msg(f"Exception Raised: Error: {error}.")
    return False


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "TAG": By.TAG_NAME,
        "CLASS": By.CLASS_NAME,
        "CSS": By.CSS_SELECTOR,
        "LINKTEXT": By.LINK_TEXT,
    }
    return map[locatorType.upper()]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:

        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag)
                )

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        return catch(e)


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for _ in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg("Exception when WaitTillElementPresent : %s" % e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        return catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        return catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))


def LoadNaukri(headless):
    """Open Chrome to load Naukri.com"""
    options = webdriver.ChromeOptions()
    if not headless:
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")  # ("--kiosk") for MAC
        options.add_argument("--disable-popups")
        options.add_argument("--disable-gpu")
    else:
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36")

    time.sleep(1.5)
    # updated to use ChromeDriverManager to match correct chromedriver automatically
    driver = None
    try:
        driver = webdriver.Chrome(options, service=ChromeService(CM().install()))
    except:
        driver = webdriver.Chrome(options)
    log_msg("Google Chrome Launched!")

    driver.implicitly_wait(3)
    driver.get(NaukriURL)
    # driver.get_screenshot_as_file("screenshot.png")
    return driver


def naukriLogin(headless=False):
    """Open Chrome browser and Login to Naukri.com"""
    status = False
    driver = None
    username_locator = "usernameField"
    password_locator = "passwordField"
    login_btn_locator = "//*[@type='submit' and normalize-space()='Login']"
    skip_locator = "//*[text() = 'SKIP AND CONTINUE']"

    try:
        driver = LoadNaukri(headless)
        if "naukri" in driver.title.lower():
            log_msg("Website Loaded Successfully.")
            # log_msg(f"WebDriver path: {ChromeDriverManager().install()}")

        emailFieldElement = None
        if is_element_present(driver, By.ID, username_locator):
            emailFieldElement = GetElement(driver, username_locator, locator="ID")
            time.sleep(1)
            passFieldElement = GetElement(driver, password_locator, locator="ID")
            time.sleep(1)
            loginButton = GetElement(driver, login_btn_locator, locator="XPATH")
        else:
            log_msg("None of the elements found to login.")

        if emailFieldElement is not None:
            emailFieldElement.clear()
            emailFieldElement.send_keys(username)
            time.sleep(1)
            passFieldElement.clear()
            passFieldElement.send_keys(password)
            time.sleep(1)
            loginButton.send_keys(Keys.ENTER)
            time.sleep(1)

            # Added click to Skip button
            print("Checking Skip button")

            if WaitTillElementPresent(driver, skip_locator, "XPATH", 10):
                GetElement(driver, skip_locator, "XPATH").click()

            # CheckPoint to verify login
            if WaitTillElementPresent(driver, "ff-inventory", locator="ID", timeout=40):
                CheckPoint = GetElement(driver, "ff-inventory", locator="ID")
                if CheckPoint:
                    log_msg("Naukri Login Successful")
                    status = True
                    return (status, driver)

                else:
                    log_msg("Unknown Login Error")
                    return (status, driver)
            else:
                log_msg("Unknown Login Error")
                return (status, driver)

    except Exception as e:
        return catch(e)
    return (status, driver)


def UpdateProfile(driver):
    try:
        mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
        saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
        view_profile_locator = "//*[contains(@class, 'view-profile')]//a"
        edit_locator = "(//*[contains(@class, 'icon edit')])[1]"
        save_confirm = "//*[text()='today' or text()='Today']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        WaitTillElementPresent(driver, view_profile_locator, "XPATH", 20)
        profElement = GetElement(driver, view_profile_locator, locator="XPATH")
        profElement.click()
        driver.implicitly_wait(2)

        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, edit_locator + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, edit_locator):
            editElement = GetElement(driver, edit_locator, locator="XPATH")
            editElement.click()

            WaitTillElementPresent(driver, mobXpath, "XPATH", 20)
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)

                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, save_confirm, "XPATH", 10)
            if is_element_present(driver, By.XPATH, save_confirm):
                log_msg("Profile Update Successful")
                return True
            else:
                log_msg("Profile Update Failed")
                return False

        elif is_element_present(driver, By.XPATH, saveXpath):
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)

                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, "confirmMessage", locator="ID", timeout=10)
            if is_element_present(driver, By.ID, "confirmMessage"):
                log_msg("Profile Update Successful")
                return True
            else:
                log_msg("Profile Update Failed")
                return False

        time.sleep(5)

    except Exception as e:
        return catch(e)


def UpdateResume():
    try:
        # random text with with random location and size
        txt = randomText()
        xloc = randint(700, 1000)  # this ensures that text is 'out of page'
        fsize = randint(1, 10)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", fsize)
        can.drawString(xloc, 100, "lon")
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(originalResumePath, "rb"))
        pagecount = len(existing_pdf.pages)
        print("Found %s pages in PDF" % pagecount)

        output = PdfWriter()
        # Merging new pdf with last page of my existing pdf
        # Updated to get last page for pdf files with varying page count
        for pageNum in range(pagecount - 1):
            output.addPage(existing_pdf.get_page_number(pageNum))

        page = existing_pdf.get_page_number(pagecount - 1)
        page.mergePage(new_pdf.get_page_number(0))
        output.addPage(page)
        # save the new resume file
        with open(modifiedResumePath, "wb") as outputStream:
            output.write(outputStream)
        print("Saved modified PDF : %s" % modifiedResumePath)
        return os.path.abspath(modifiedResumePath)
    except Exception as e:
        return os.path.abspath(originalResumePath)


def UploadResume(driver, resumePath):
    try:
        attachCVID = "attachCV"
        CheckPointXpath = "//*[contains(@class, 'updateOn')]"
        saveXpath = "//button[@type='button']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        driver.get("https://www.naukri.com/mnjuser/profile")

        time.sleep(2)
        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, attachCVID, locator="ID", timeout=10)
        AttachElement = GetElement(driver, attachCVID, locator="ID")
        AttachElement.send_keys(resumePath)

        if WaitTillElementPresent(driver, saveXpath, locator="ID", timeout=5):
            saveElement = GetElement(driver, saveXpath, locator="XPATH")
            saveElement.click()

        WaitTillElementPresent(driver, CheckPointXpath, locator="XPATH", timeout=30)
        CheckPoint = GetElement(driver, CheckPointXpath, locator="XPATH")
        if CheckPoint:
            LastUpdatedDate = CheckPoint.text
            todaysDate1 = datetime.today().strftime("%b %d, %Y")
            todaysDate2 = datetime.today().strftime("%b %#d, %Y")
            if todaysDate1 in LastUpdatedDate or todaysDate2 in LastUpdatedDate:
                log_msg(
                    "Resume Document Upload Successful. Last Updated date = %s"
                    % LastUpdatedDate
                )
                log_msg(f"Update time: {datetime.now()}")
                return True
            else:
                log_msg(
                    "Resume Document Upload failed. Last Updated date = %s"
                    % LastUpdatedDate
                )
                return False
        else:
            log_msg("Resume Document Upload failed. Last Updated date not found.")

    except Exception as e:
        return catch(e)
    time.sleep(2)


def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin(headless=headless_mode)
        if status:
            UpdateProfile(driver)
            if os.path.exists(originalResumePath):
                if updatePDF:
                    resumePath = UpdateResume()
                    return UploadResume(driver, resumePath)
                else:
                    return UploadResume(driver, originalResumePath)
            else:
                log_msg("Resume not found at %s " % originalResumePath)
                return False

    except Exception as e:
        log_msg(f"Error: {e}")
        return catch(e)

    finally:
        tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")


def clear_output_file():
    # Open the file in write mode to truncate it
    naukri_log = "naukri.log"
    with open(naukri_log, 'w'):
        pass  # No need to do anything, the file will be truncated

    nohup_file = "nohup.out"
    with open(nohup_file, 'w'):
        pass  # No need to do anything, the file will be truncated


def job():
    try:
        log_msg("Job execution started.")
        success = main()
        log_msg(f"Job Response: {success}")
        if success:
            return True
        return False
    except Exception as e:
        return catch(e)


def retry_job():
    success = job()
    log_msg(f"Retry Job Response: {success}")
    if success:
        log_msg("Job execution finished, Clearing the retry_job")
        # If the retry job succeeds, clear the retry schedule
        schedule.clear('retry_job')
        log_msg("Retry job cleared.")
    if not success:
        log_msg(f"Retry job also failed, It will retry again in {retry_time} minutes")


def schedule_main_job():
    clear_output_file()
    success = job()
    log_msg(f"Scheduled Job Response: {success}")
    if success:
        log_msg("Job execution finished, Resume Updated.")
    if not success:
        log_msg(f"Job execution failed, Scheduling retry job for every {retry_time} minutes.")
        # Tag the retry job so it can be cleared later
        schedule.every(retry_time).minutes.do(retry_job).tag('retry_job')
        log_msg("Retry job scheduled.")


# Initial scheduling of the main job
execution_slots_str = os.getenv("execution_time_slots")
execution_time_slots = eval(execution_slots_str)
for execution_time in execution_time_slots:
    schedule.every().day.at(str(execution_time)).do(schedule_main_job)

while True:
    log_msg(f"Checking job scheduler: Time: {datetime.now()}")
    schedule.run_pending()
    time.sleep(10 * 30)  # check & schedule job after every 20 minutes
