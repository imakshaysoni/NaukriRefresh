import logging
import io
import os
import sys
import time
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits
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


class Naukri:
    def __init__(self):
        self.url = "https://www.naukri.com/nlogin/login"
        self.driver = self.LoadNaukri()

    @staticmethod
    def catch(error):
        """Method to self.catch errors and log error details"""
        _, _, exc_tb = sys.exc_info()
        lineNo = str(exc_tb.tb_lineno)
        msg = "%s : %s at Line %s." % (type(error), error, lineNo)
        logging.error(msg)
        logging.error(f"Exception Raised: Error: {error}.")
        return False

    def getObj(self, locatorType):
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

    def _get_element(self, _tag, _locator):
        _by = self.getObj(_locator)
        if self.is_element_present(_by, _tag):
            return WebDriverWait(self.driver, timeout=15).until(
                lambda d: self.driver.find_element(_by, _tag)
            )

    def GetElement(self, elementTag, locator="ID"):
        """Wait max 15 secs for element and then select when it is available"""
        try:
            element = self._get_element(elementTag, locator.upper())
            if element:
                return element
            else:
                logging.info("Element not found with %s : %s" % (locator, elementTag))
                return None
        except Exception as e:
            return self.catch(e)

    def is_element_present(self, how, what):
        """Returns True if element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def WaitTillElementPresent(self, elementTag, locator="ID", timeout=30):
        """Wait till element present. Default 30 seconds"""
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()

        for _ in range(timeout):
            time.sleep(0.99)
            try:
                if self.is_element_present(self.getObj(locator), elementTag):
                    result = True
                    break
            except Exception as e:
                logging.info("Exception when WaitTillElementPresent : %s" % e)
                pass

        if not result:
            logging.info("Element not found with %s : %s" % (locator, elementTag))
        self.driver.implicitly_wait(3)
        return result

    def tearDown(self):
        try:
            self.driver.close()
            logging.info("self.driver Closed Successfully")
        except Exception as e:
            return self.catch(e)
            pass

        try:
            self.driver.quit()
            logging.info("self.driver Quit Successfully")
        except Exception as e:
            return self.catch(e)
            pass

    @staticmethod
    def randomText():
        return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))

    def LoadNaukri(self, headless=False):
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
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36"
            )

        time.sleep(1.5)
        # updated to use Chromeself.driverManager to match correct chromeself.driver automatically
        driver = None
        try:
            driver = webdriver.Chrome(options, service=ChromeService(CM().install()))
        except:
            driver = webdriver.Chrome(options)
        logging.info("Google Chrome Launched!")

        driver.implicitly_wait(3)
        driver.get(self.url)
        # driver.get_screenshot_as_file("screenshot.png")
        return driver

    def naukriLogin(self, username, password, headless=False):
        """Open Chrome browser and Login to Naukri.com"""
        status = False
        username_locator = "usernameField"
        password_locator = "passwordField"
        login_btn_locator = "//*[@type='submit' and normalize-space()='Login']"
        skip_locator = "//*[text() = 'SKIP AND CONTINUE']"

        try:
            if "naukri" in self.driver.title.lower():
                logging.info("Website Loaded Successfully.")
                # logging.info(f"Webdriver path: {ChromedriverManager().install()}")

            emailFieldElement = None
            if self.is_element_present(By.ID, username_locator):
                emailFieldElement = self.GetElement(username_locator, locator="ID")
                time.sleep(1)
                passFieldElement = self.GetElement(password_locator, locator="ID")
                time.sleep(1)
                loginButton = self.GetElement(login_btn_locator, locator="XPATH")
            else:
                logging.info("None of the elements found to login.")

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

                if self.WaitTillElementPresent(skip_locator, "XPATH", 10):
                    self.GetElement(skip_locator, "XPATH").click()

                # CheckPoint to verify login
                if self.WaitTillElementPresent(
                    "ff-inventory", locator="ID", timeout=40
                ):
                    CheckPoint = self.GetElement("ff-inventory", locator="ID")
                    if CheckPoint:
                        logging.info("Naukri Login Successful")
                        status = True
                        return (status, self.driver)

                    else:
                        logging.info("Unknown Login Error")
                        return (status, self.driver)
                else:
                    logging.info("Unknown Login Error")
                    return (status, self.driver)

        except Exception as e:
            return self.catch(e)
        return (status, self.driver)

    def UpdateProfile(self, mobile_number):
        try:
            mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
            saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
            view_profile_locator = "//*[contains(@class, 'view-profile')]//a"
            edit_locator = "(//*[contains(@class, 'icon edit')])[1]"
            save_confirm = "//*[text()='today' or text()='Today']"
            close_locator = "//*[contains(@class, 'crossIcon')]"

            self.WaitTillElementPresent(view_profile_locator, "XPATH", 20)
            profElement = self.GetElement(view_profile_locator, locator="XPATH")
            profElement.click()
            self.driver.implicitly_wait(2)

            if self.WaitTillElementPresent(close_locator, "XPATH", 10):
                self.GetElement(close_locator, locator="XPATH").click()
                time.sleep(2)

            self.WaitTillElementPresent(edit_locator + " | " + saveXpath, "XPATH", 20)
            if self.is_element_present(By.XPATH, edit_locator):
                editElement = self.GetElement(edit_locator, locator="XPATH")
                editElement.click()

                self.WaitTillElementPresent(mobXpath, "XPATH", 20)
                mobFieldElement = self.GetElement(mobXpath, locator="XPATH")
                if mobFieldElement:
                    mobFieldElement.clear()
                    mobFieldElement.send_keys(mobile_number)
                    self.driver.implicitly_wait(2)

                    saveFieldElement = self.GetElement(saveXpath, locator="XPATH")
                    saveFieldElement.send_keys(Keys.ENTER)
                    self.driver.implicitly_wait(3)
                else:
                    logging.info("Mobile number element not found in UI")

                self.WaitTillElementPresent(save_confirm, "XPATH", 10)
                if self.is_element_present(By.XPATH, save_confirm):
                    logging.info("Profile Update Successful")
                    return True
                else:
                    logging.info("Profile Update Failed")
                    return False

            elif self.is_element_present(By.XPATH, saveXpath):
                mobFieldElement = self.GetElement(mobXpath, locator="XPATH")
                if mobFieldElement:
                    mobFieldElement.clear()
                    mobFieldElement.send_keys(mobile_number)
                    self.driver.implicitly_wait(2)

                    saveFieldElement = self.GetElement(saveXpath, locator="XPATH")
                    saveFieldElement.send_keys(Keys.ENTER)
                    self.driver.implicitly_wait(3)
                else:
                    logging.info("Mobile number element not found in UI")

                self.WaitTillElementPresent("confirmMessage", locator="ID", timeout=10)
                if self.is_element_present(By.ID, "confirmMessage"):
                    logging.info("Profile Update Successful")
                    return True
                else:
                    logging.info("Profile Update Failed")
                    return False

            time.sleep(5)

        except Exception as e:
            return self.catch(e)

    def UpdateResume(self, resume_path):
        try:
            # random text with with random location and size
            self.randomText()
            xloc = randint(700, 1000)  # this ensures that text is 'out of page'
            fsize = randint(1, 10)

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont("Helvetica", fsize)
            can.drawString(xloc, 100, "lon")
            can.save()

            packet.seek(0)
            new_pdf = PdfReader(packet)
            existing_pdf = PdfReader(open(resume_path, "rb"))
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
            with open(resume_path, "wb") as outputStream:
                output.write(outputStream)
            print("Saved modified PDF : %s" % resume_path)
            return os.path.abspath(resume_path)
        except Exception:
            return os.path.abspath(resume_path)

    def UploadResume(self, resumePath):
        try:
            attachCVID = "attachCV"
            CheckPointXpath = "//*[contains(@class, 'updateOn')]"
            saveXpath = "//button[@type='button']"
            close_locator = "//*[contains(@class, 'crossIcon')]"

            self.driver.get("https://www.naukri.com/mnjuser/profile")

            time.sleep(2)
            if self.WaitTillElementPresent(close_locator, "XPATH", 10):
                self.GetElement(close_locator, locator="XPATH").click()
                time.sleep(2)

            self.WaitTillElementPresent(attachCVID, locator="ID", timeout=10)
            AttachElement = self.GetElement(attachCVID, locator="ID")
            AttachElement.send_keys(resumePath)

            if self.WaitTillElementPresent(saveXpath, locator="ID", timeout=5):
                saveElement = self.GetElement(saveXpath, locator="XPATH")
                saveElement.click()

            self.WaitTillElementPresent(CheckPointXpath, locator="XPATH", timeout=30)
            CheckPoint = self.GetElement(CheckPointXpath, locator="XPATH")
            if CheckPoint:
                LastUpdatedDate = CheckPoint.text
                todaysDate1 = datetime.today().strftime("%b %d, %Y")
                todaysDate2 = datetime.today().strftime("%b %#d, %Y")
                if todaysDate1 in LastUpdatedDate or todaysDate2 in LastUpdatedDate:
                    logging.info(
                        "Resume Document Upload Successful. Last Updated date = %s"
                        % LastUpdatedDate
                    )
                    logging.info(f"Update time: {datetime.now()}")
                    return True
                else:
                    logging.info(
                        "Resume Document Upload failed. Last Updated date = %s"
                        % LastUpdatedDate
                    )
                    return False
            else:
                logging.info(
                    "Resume Document Upload failed. Last Updated date not found."
                )

        except Exception as e:
            return self.catch(e)
        time.sleep(2)

    def run(self, user_name, password, mobile_number, resume_path, updatePDF=True):
        logging.info("-----Naukri.py Script Run Begin-----")
        try:
            status, self.driver = self.naukriLogin(
                username=user_name, password=password
            )
            if status:
                self.UpdateProfile(mobile_number)
                if os.path.exists(resume_path):
                    if updatePDF:
                        resumePath = self.UpdateResume(resume_path)
                        return self.UploadResume(resumePath)
                    else:
                        return self.UploadResume(resume_path)
                else:
                    logging.info("Resume not found at %s " % resume_path)
                    return False

        except Exception as e:
            logging.info(f"Error: {e}")
            return self.catch(e)

        finally:
            self.tearDown()

        logging.info("-----Naukri.py Script Run Ended-----\n")
