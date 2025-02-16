import os
import tempfile
import shutil
from FileUtils import relative_path
import re
import time

class FileInfo(object):


    def __init__(self):
        # Path to the /data directory
        self.data_path = relative_path(path_to_append="\\..\\data")

        # TemporaryDirectory object for backups
        self.td_backup_dir = tempfile.mkdtemp(dir=self.data_path)

        # Path to temporary directory
        self.backup_path = str(self.td_backup_dir)


    def make_data_backup(self):
        # Make a backup of the current csv files
        self.copy_csv()

        # Delete the current CSV files from /data
        self.delete_csv()


    def restore_data_backup(self):
        # Clear any partial downloads from /data
        self.delete_csv()

        # Move files from temp directory to /data
        for file in os.listdir(self.backup_path):
            file_path = self.backup_path + "\\" + file
            shutil.move(file_path, self.data_path)

        self.backup_path.cleanup()


    def download_successful(self):
        # Checks the /data directory for exactly three
        #  .csv files
        dup_pattern = r"\(\d+\)"
        count = 0
        if self.wait_for_download(".csv"):
            for file in os.listdir(self.data_path):
                if file.endswith(".csv") and re.search(dup_pattern, file) == None:
                    count += 1
                else:
                    count -= 1
            
        return count == 3
    

    def wait_for_download(self, filename, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if any(f.endswith(filename) for f in os.listdir(self.data_path)):
                print("Download complete!")
                return True
            time.sleep(1)
        print("Timeout: File not found.")
        return False



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

        self.backup_path.cleanup()