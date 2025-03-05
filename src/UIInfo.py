
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from WebUtils import initialize_fetch_csv
import threading
import queue
import time
import FileInfo
import FileUtils
import ClassifyUtils

class UIInfo (object):
    
    def __init__(self):
        """
        Initialize the user interface for the Pokémon ranking search application.

        :param data: The dataset containing Pokémon rankings.
        """

        self.csv_data = FileUtils.load_data()
        self.suggestion_buttons = []
        self.except_queue = queue.Queue()

        self.root = tk.Tk()
        self.root.title("Go Battle League Pokémon Ranking")
        self.root.geometry("600x500")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.grid_columnconfigure(0, weight=0)  # Left-aligned elements (labels, checkboxes, bottom_frame)
        self.frame.grid_columnconfigure(1, weight=1)  # Search entry should expand
        self.frame.grid_columnconfigure(2, weight=0)  # Right-side elements (buttons)
        self.frame.grid_rowconfigure(99, weight=1)  # Push bottom_frame to the bottom

        self.download_frame = ttk.Frame(self.frame)
        self.download_frame.grid(row=99, column=0, columnspan=2, sticky=tk.SW)

        self.search_label = ttk.Label(self.frame, text="Enter Pokémon Name:")
        self.search_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.download_label = ttk.Label(self.frame, text="", foreground="blue")
        self.download_label.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)

        self.search_entry = ttk.Entry(self.frame, width=50)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.search_entry.focus_set()

        self.search_button = ttk.Button(self.frame, text="Search", command=lambda: self.search_pokemon())
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.result_label = ttk.Label(self.frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W)
        self.result_label.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        self.download_assets_button = ttk.Button(self.download_frame, text="Download Assets")
        self.download_assets_button.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)
        self.download_assets_button.config(command=lambda: self.download_assets())

        self.download_label = ttk.Label(self.download_frame, text="", foreground="blue")
        self.download_label.grid(row=0, column=1, padx=5, pady=1, sticky=tk.W)

        # Checkbox for displaying other league scores (initially hidden)
        self.do_show_all_ranks = tk.BooleanVar(value=False)
        self.show_all_ranks_checkbox = ttk.Checkbutton(
                        self.frame, 
                        text="Show scores in other leagues", 
                        variable=self.do_show_all_ranks,
                        command=lambda: self.search_pokemon()
                    )
        
        self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
        self.show_all_ranks_checkbox.grid_remove()  # Hide initially

        # Frame for displaying suggestions
        self.suggestions_frame = ttk.Frame(self.frame)
        self.suggestions_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        self.root.bind('<Return>', lambda event: self.search_pokemon())
        self.root.mainloop()


    def search_pokemon(self):
        """
        Search for a Pokémon in the dataset and display its ranking or suggestions.

        :param data: The dataset containing Pokémon rankings.
        :param ui_info: The UIInfo object containing references to UI elements.
        """
        supplied_name = self.search_entry.get().strip().lower()

        if not supplied_name:
            messagebox.showwarning("Input Error", "Please enter a Pokémon name.")
            return

        # Clear previous search results
        self.result_label.config(text="")
        self.clear_suggestion_buttons()
        self.show_all_ranks_checkbox.grid_remove()  # Hide checkbox initially

        # Initialize classification variables
        best_score = float('-inf')
        best_rank = float('inf')
        best_league = None
        rank_scores = []  # Holds scores from all leagues

        # Search for the Pokémon in all leagues
        for league_name, league_data in self.csv_data.items():
            result = league_data[league_data['Pokemon'].str.lower() == supplied_name]
            if not result.empty:
                score = result.at[result.index[0], 'Score']
                rank = result.index[0] + 1

                # Store other rankings for later use
                rank_scores.append(f"{league_name.capitalize()} League: Rank #{rank} (Score: {score})")

                # Track best ranking
                if rank < best_rank:
                    best_rank = rank
                    best_score = score
                    best_league = league_name

        # If Pokémon was found
        if best_league:
            best_result_text = (f"{supplied_name.capitalize()} is ranked #{best_rank} "
                                f"with a score of {best_score} in the {best_league.capitalize()} League.")
            
            # Remove best_league from rank_scores list
            rank_scores = [entry for entry in rank_scores if not entry.startswith(f"{best_league.capitalize()} League")]

            # Sort remaining leagues by highest rank (lowest rank number first)
            rank_scores.sort(key=lambda entry: int(entry.split("#")[1].split()[0]))

            # If the checkbox is checked, show all league ranks
            if self.do_show_all_ranks.get() and rank_scores:
                best_result_text += "\n\nOther leagues:\n" + "\n".join(rank_scores)

            self.result_label.config(text=best_result_text)
            self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)  # Show checkbox

        # If Pokémon was not found, suggest similar names
        else:
            suggestions = ClassifyUtils.suggest_similar_names(supplied_name, self.csv_data)
            if suggestions:
                self.display_suggestions(supplied_name, suggestions)
            else:
                self.result_label.config(text=f"{supplied_name.capitalize()} not found in any league.")

        # Focus and select all text in the search entry
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)


    def display_suggestions(self, pokemon_name, suggestions):
        """
        Display the suggestions as clickable buttons under the result label.

        :param pokemon_name: The name of the Pokémon searched by the user.
        :param suggestions: List of suggested Pokémon names.
        :param ui_info: The UIInfo object containing references to UI elements.
        :param data: The data dictionary with league information.
        """
        # Display the "not found" message
        self.result_label.config(text=f"{pokemon_name.capitalize()} not found in any league.\nDid you mean one of these?")

        # Clear any previous suggestion buttons
        self.suggestion_buttons.clear()

        # Create buttons for each suggestion using grid
        for idx, name in enumerate(suggestions):
            button = ttk.Button(
                self.result_label.master,  # Parent widget
                text=name,
                command=lambda n=name: self.search_entry.delete(0, tk.END) or self.search_entry.insert(0, n) or self.search_pokemon()
            )
            button.grid(row=idx + 2, column=0, columnspan=3, pady=5, sticky=tk.EW)  # Adjust positioning
            self.suggestion_buttons.append(button)  # Track the button


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

                while not self.except_queue.empty():
                    ecode = self.except_queue.get()
                    if ecode != None:
                        self.download_label.config(text=f"Download failed.", foreground="red")
                        file_info.restore_data_backup()
                        return

                self.csv_data = FileUtils.load_data()
                self.download_label.config(text=f"Download complete.")
                file_info.discard_backup()

            except Exception as e:
                self.download_label.config(text=f"Error: {e}", foreground="red")
            finally:
                self.reenable_ui()

        self.download_label.config(text=f"Downloading assets...", foreground="blue")
        self.disable_ui()

        fetch_thread = threading.Thread(target=perform_download)
        fetch_thread.start()