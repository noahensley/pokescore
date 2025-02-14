import sys
import os.path
import re


def get_driver_file_path():
    """
    Gets the relative path to the chromedriver executable.

    Returns:
        str: The relative path to chromedriver executable.

    Raises:
        RuntimeError: If the generated path is invalid.
    """
    # Assigns cwd based on execution mode
    if getattr(sys, 'frozen', False):
        cwd = os.path.dirname(sys.executable)
    elif __file__:
        cwd = os.path.dirname(__file__)
    
    # Creates a relative path to the chromedriver executable
    driver_path = os.path.join(cwd, '..', 'utils', 'chromedriver-win64', "chromedriver.exe")

    # Checks that the generated path is valid
    if os.path.isfile(driver_path):
        return driver_path
    
    raise RuntimeError("Invalid driver path")


def copy_csv():
    # Make a copy of the CSV files currently in the /data
    #  directory to return if download incomplete
    pass


def restore_csv():
    # Restore the copied CSV files in case of a bad
    #  download
    pass

