import sys
import os.path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import threading
import time
import re
import FileInfo
from pathlib import Path
from FileUtils import wait_for_download

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import core


def initialize_fetch_csv():

    fi = FileInfo.FileInfo()
    fi.make_data_backup()

    gl_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(core.urls["great"],fi.data_path,))
    ul_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(core.urls["ultra"],fi.data_path,))
    ml_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(core.urls["master"],fi.data_path,))
    
    gl_csv_thread.start()
    ul_csv_thread.start()
    ml_csv_thread.start()

    gl_csv_thread.join()
    ul_csv_thread.join()
    ml_csv_thread.join()

    if not fi.downloads_successful():
        fi.restore_data_backup()


def fetch_csv(src, dst):
    if type(src) != str:
        raise TypeError("Input URL must be a string.")
    
    match = re.search(core.pattern, src)

    if not match:
        raise RuntimeError("Unsupported URL format.")

    try:
        # Initialize webdriver
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-usb-discovery")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": os.path.abspath(dst),  # Set download directory
            "download.prompt_for_download": False,  # Auto-download files
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        driver.get(src)

        # Download CSV data
        try:
            export_hyperlink = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Export to CSV")))
            export_hyperlink.click()
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error: Export link not found or not clickable - {e}")

    except WebDriverException as e:
        print(f"WebDriver error: {e}")

    except (FileNotFoundError, PermissionError) as e:
        print(f"File system error: {e}")

    except (ElementClickInterceptedException, StaleElementReferenceException) as e:
        print(f"Element error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        wait_for_download(url=src, dst=dst)
        if 'driver' in locals():
            driver.quit()  # Ensures cleanup even if an error occurs

    
initialize_fetch_csv()


    