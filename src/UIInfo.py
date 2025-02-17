
import tkinter as tk
from WebUtils import initialize_fetch_csv
import threading
import queue
import time
import FileInfo

class UIInfo (object):
    def __init__(self, root, frame, download_frame, suggestions_frame,
                 search_label, search_button, search_entry, result_label, 
                 download_button, download_label, 
                 do_show_all_ranks, show_all_ranks_checkbox):
        
        self.root = root
        self.frame = frame
        self.download_frame = download_frame
        self.search_label = search_label
        self.search_button = search_button
        self.search_entry = search_entry
        self.result_label = result_label
        self.suggestions_frame = suggestions_frame
        self.do_show_all_ranks = do_show_all_ranks
        self.show_all_ranks_checkbox = show_all_ranks_checkbox
        self.suggestion_buttons = []  # List to track suggestion buttons
        self.download_assets_button = download_button
        self.download_label = download_label
        self.except_queue = queue.Queue()
        self.completed_lock = threading.Lock()
        self.completed_threads = 0

    def clear_suggestion_buttons(self):
        for button in self.suggestion_buttons:
            button.destroy()  # Remove the button from the UI
        self.suggestion_buttons.clear()  # Clear the list


    def disable_ui(self):
        """Disable UI elements during download."""
        self.search_entry.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        self.download_assets_button.config(state=tk.DISABLED)
        self.disable_close()  # Disable close button


    def reenable_ui(self):
        """Re-enable UI elements after download."""
        self.search_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.download_assets_button.config(state=tk.NORMAL)
        self.reenable_close()  # Restore close button


    def disable_close(self):
            """Disable the window's close (X) button."""
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # Ignore close button


    def reenable_close(self):
        """Re-enable the close button after download finishes."""
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)  # Restore normal behavior

    def download_assets(self):

        def perform_download():
            """Perform the actual file download and update UI accordingly."""
            try:
                file_info = FileInfo.FileInfo()
                file_info.make_data_backup()

                initialize_fetch_csv(self.except_queue, file_info)

                while self.except_queue.qsize() < 3:
                    #print("waiting for thread to finish")
                    time.sleep(0.5)
             
                ecode = self.except_queue.get()

                if ecode != None:
                    self.download_label.config(text=f"Download failed. Error: {ecode}")
                    file_info.restore_data_backup()
                else:
                    self.download_label.config(text=f"Download complete.")
                    file_info.discard_backup()

            except Exception as e:
                self.download_label.config(text=f"Error: {e}", foreground="red")
            finally:
                self.reenable_ui()

        self.download_label.config(text=f"Downloading assets...")
        self.disable_ui()

        fetch_thread = threading.Thread(target=perform_download)
        fetch_thread.start()