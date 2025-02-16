import os
import tempfile
import shutil
from FileUtils import relative_path
import re


class FileInfo(object):


    def __init__(self):
        # Path to the /data directory
        self.data_path = relative_path(path_to_append="\\..\\data")

        # Path to temporary directory
        self.backup_path = tempfile.mkdtemp(dir=self.data_path)


    def make_data_backup(self):
        # Make a backup of the current csv files
        self.copy_csv()

        # Delete the current CSV files from /data
        self.delete_csv()


    def restore_data_backup(self):
        # Clear any partial downloads from /data
        self.delete_csv()

        # Move files from temp directory to /data
        self.restore_csv()

        os.rmdir(self.backup_path)


    def download_successful(self):
        # Checks the /data directory for exactly three
        #  .csv files
        dup_pattern = r"\(\d+\)"
        count = 0
        for file in os.listdir(self.data_path):
            if file.endswith(".csv") and re.search(dup_pattern, file) == None:
                count += 1
            else:
                count -= 1
            
        return count == 3


    # Make a copy of the CSV files currently in /data
    def copy_csv(self):
        for file in os.listdir(self.data_path):
            if file.endswith(".csv"):
                file_path = self.data_path + "\\" + file
                shutil.copy2(file_path, self.backup_path)

    
    # Clear the entire contents of the /data directory.
    #  Used before restoring after an unsuccessful down-
    #  load.
    def delete_csv(self):
        for file in os.listdir(self.data_path):
            if not file.endswith(".gitignore"):
                file_path = self.data_path + "\\" + file
                # Ignores the temp dir
                if os.path.isfile(file_path):
                    os.remove(file_path)


    # Restore the copy of CSV files from the temp directory
    def restore_csv(self):
        for file in os.listdir(self.backup_path):
            if file.endswith(".csv"):
                file_path = self.backup_path + "\\" + file
                shutil.move(file_path, self.data_path)