import sys
import os.path

def get_relative_cwd():
    # Assigns cwd based on execution mode
    if getattr(sys, 'frozen', False):
        cwd = os.path.dirname(sys.executable)
    elif __file__:
        cwd = os.path.dirname(__file__)

    return cwd

