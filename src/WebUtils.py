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
from FileUtils import get_driver_file_path
import threading
import time
import re


pattern = r"https://pvpoke\.com/rankings/all/(\d{4,5})/overall/"


def initialize_fetch_csv():
    gl_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=("https://pvpoke.com/rankings/all/1500/overall/",))
    ul_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=("https://pvpoke.com/rankings/all/2500/overall/",))
    ml_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=("https://pvpoke.com/rankings/all/10000/overall/",))
    
    gl_csv_thread.start()
    ul_csv_thread.start()
    ml_csv_thread.start()

    gl_csv_thread.join()
    ul_csv_thread.join()
    ml_csv_thread.join()


def wait_for_download(filename, download_dir, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if any(f.endswith(filename) for f in os.listdir(download_dir)):
            print("Download complete!")
            return True
        time.sleep(1)
    print("Timeout: File not found.")
    return False


def format_csv_filename(url):
    if type(url) != str:
        raise TypeError("Input URL must be a string.")
    
    match = re.search(pattern, url)

    if not match:
        raise RuntimeError("Unsupported URL format.")
    
    url = url.split("/")
    fname = []
    fname.append("cp" + url[5])
    fname.append(url[4])
    fname.append(url[6])
    
    return "_".join(fname)


def fetch_csv(url):
    if type(url) != str:
        raise TypeError("Input URL must be a string.")
    
    match = re.search(pattern, url)

    if not match:
        raise RuntimeError("Unsupported URL format.")

    download_dir = os.getcwd() + "\\data"
    # copy_csv()

    try:
        # Initialize webdriver
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-usb-discovery")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,  # Set download directory
            "download.prompt_for_download": False,  # Auto-download files
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        # Export CSV data
        try:
            export_hyperlink = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Export to CSV")))
            export_hyperlink.click()
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error: Export link not found or not clickable - {e}")
        
        if wait_for_download(format_csv_filename(url), download_dir) == False:
            # restore_csv()
            pass

    except WebDriverException as e:
        print(f"WebDriver error: {e}")

    except (FileNotFoundError, PermissionError) as e:
        print(f"File system error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if 'driver' in locals():
            driver.quit()  # Ensures cleanup even if an error occurs


initialize_fetch_csv()


    