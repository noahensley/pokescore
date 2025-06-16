import os
import sys
import time
import re
from tkinter import messagebox
import pandas as pd

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
    
    match = re.search(core.url_pattern, url)

    if not match:
        raise RuntimeError("Unsupported URL format.")
    
    url = url.split("/")
    fname = []
    fname.append("cp" + url[5])
    fname.append(url[4])
    fname.append(url[6])
    fname.append("rankings")

    return "_".join(fname) + ".csv"


def load_data():
    """
    Load Pokémon ranking data from CSV files for various leagues.

    :return: A dictionary with league names as keys and Pandas DataFrames as values.
    """
    try:
        # Import .csv rankings from pvpoke.com
        target_dir = relative_path(path_to_append="\\..\\data")
        great_league = pd.read_csv(os.path.join(target_dir, 'cp1500_all_overall_rankings.csv'))
        ultra_league = pd.read_csv(os.path.join(target_dir, 'cp2500_all_overall_rankings.csv'))
        master_league = pd.read_csv(os.path.join(target_dir, 'cp10000_all_overall_rankings.csv'))

        return {
            'great': great_league,
            'ultra': ultra_league,
            'master': master_league
        }
    except FileNotFoundError as e:
        messagebox.showerror("File Not Found", f"Could not find file: {e.filename}")
        exit()
