import sys
import time
import re

from pathlib import Path

base_path = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
sys.path.append(str(base_path))
sys.path.append(str(base_path.parent))

from utils import core


def relative_path(path_to_append=""):
    base_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
    cwd = str(base_dir) + path_to_append
    return cwd


def format_csv_filename(url):
    if type(url) != str:
        raise TypeError("Input URL must be a string.")
    
    match = re.search(core.pattern, url)

    if not match:
        raise RuntimeError("Unsupported URL format.")
    
    url = url.split("/")
    fname = []
    fname.append("cp" + url[5])
    fname.append(url[4])
    fname.append(url[6])
    fname.append("rankings")

    return "_".join(fname) + ".csv"


def wait_for_download(url, dst, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if any(f == format_csv_filename(url) for f in os.listdir(dst)):
            print("Download complete!")
            return True
        time.sleep(1)
    print("Timeout: File not found.")
    return False
