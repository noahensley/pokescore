import sys
import os.path

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
import re
from pathlib import Path

base_path = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
sys.path.append(str(base_path))
sys.path.append(str(base_path.parent))

from utils import core


def initialize_fetch_csv(q, fi):

    gl_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(q,core.urls["great"],fi.data_path,))
    ul_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(q,core.urls["ultra"],fi.data_path,))
    ml_csv_thread = threading.Thread(target=fetch_csv, 
                                     args=(q,core.urls["master"],fi.data_path,))
    
    gl_csv_thread.start()
    ul_csv_thread.start()
    ml_csv_thread.start()

    gl_csv_thread.join()
    ul_csv_thread.join()
    ml_csv_thread.join()        


def fetch_csv(q, src, dst):
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
        chrome_options.add_argument("--disable-device-discovery-notifications")
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
        export_hyperlink = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Export to CSV")))
        export_hyperlink.click()

    except Exception as e:
        print(f"Unexpected error: {e}")
        q.put(e)

    finally:
        time.sleep(2) # Wait for download to complete
        if 'driver' in locals():
            driver.quit()  # Ensures cleanup even if an error occurs

    q.put(None)


    