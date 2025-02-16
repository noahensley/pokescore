from pathlib import Path
import sys


def relative_path(path_to_append=""):
    base_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

    cwd = str(base_dir) + path_to_append
    
    return cwd
