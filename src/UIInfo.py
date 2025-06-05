
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from WebUtils import initialize_fetch_csv
import threading
import queue
import FileInfo
import FileUtils
import ClassifyUtils

class UIInfo (object):
    
    def __init__(self):

        self.csv_data = FileUtils.load_data()
        self.suggestion_buttons = []
        self.except_queue = queue.Queue()
        self.result_info = {}

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

        # Logic/checkbox for displaying other league scores (initially hidden)
        self.do_show_all_ranks = tk.BooleanVar(value=False)
        self.show_all_ranks_checkbox = ttk.Checkbutton(
                        self.frame, 
                        text="Show scores in other leagues",
                        variable=self.do_show_all_ranks,
                        command=lambda: self.populate_result_label()
                    )
        
        # Logic/checkbox for displaying moveset (initially hidden)
        self.do_show_moveset = tk.BooleanVar(value=False)
        self.show_moveset_checkbox = ttk.Checkbutton(
                        self.frame,
                        text="Show moveset",
                        variable=self.do_show_moveset,
                        command=lambda: self.populate_result_label()
                    )
        
        self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
        self.show_all_ranks_checkbox.grid_remove()  # Hide initially
        self.show_moveset_checkbox.grid(row=3, column=0, columnspan=3, pady=5, stick=tk.W)
        self.show_moveset_checkbox.grid_remove()

        # Frame for displaying suggestions
        self.suggestions_frame = ttk.Frame(self.frame)
        self.suggestions_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # Allow user to press 'Enter' to search
        self.root.bind('<Return>', lambda event: self.search_pokemon())
        self.root.mainloop()


    def search_pokemon(self):
        """
        Search for a Pokémon in the dataset and assign reults to 'result_info' attribute.
        """
        supplied_name = self.search_entry.get().strip().lower()

        if not supplied_name:
            messagebox.showwarning("Input Error", "Please enter a Pokémon name.")
            return

        # Clear previous search results
        self.result_label.config(text="")
        self.clear_suggestion_buttons()
        # Hide checkboxes each search
        self.show_all_ranks_checkbox.grid_remove()
        self.show_moveset_checkbox.grid_remove()

        # Initialize classification variables
        self.result_info['Other Leagues'] = {}
        search_result_data = None

        # Search for the Pokémon in all leagues
        for league_name, league_data in self.csv_data.items():
            search_result_data = league_data[league_data['Pokemon'].str.lower() == supplied_name]
            if not search_result_data.empty:
                cur_index = search_result_data.index[0]
                score = search_result_data.at[cur_index, 'Score']
                rank = cur_index + 1 # Use row/index to calculate rank

                # Store current league information
                m_fast = search_result_data.at[cur_index, 'Fast Move']
                m_charged1 = search_result_data.at[cur_index, 'Charged Move 1']
                m_charged2 = search_result_data.at[cur_index, 'Charged Move 2']
                self.result_info['Other Leagues'][league_name.capitalize()] = (
                    (rank, score), 
                    {'Fast': m_fast, 'Charged1': m_charged1, 'Charged2': m_charged2}
                )

        # If Pokémon was found, determine best league and remove it from 'Other Leagues'
        if self.compare_rankings(supplied_name):       
            # Display 'other leagues' checkbox
            self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
            # Display 'moveset' checkbox
            self.show_moveset_checkbox.grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Display results or display suggestions
        self.populate_result_label()

        # Focus and select all text in the search entry
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)


    def display_suggestions(self, suggestions):
        """
        Display suggested Pokémon as clickable buttons under the result label.

        :param suggestions: List of suggested Pokémon names.
        """
        # Clear any previous suggestion buttons
        self.suggestion_buttons.clear()

        # Display the "not found" message
        self.result_label.config(text=f"{self.result_info['Name']} not found in any League.\nDid you mean one of these?")

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
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # Ignore close button presses


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


    def populate_result_label(self):
        result_text = ""
        if not self.result_info:
            self.result_label.config(text=result_text)
            return
        
        if not self.result_info['Found']:
            suggestions = ClassifyUtils.suggest_similar_names(self.result_info['Name'], self.csv_data)
            if suggestions:
                self.display_suggestions(suggestions)
            else:
                self.result_label.config(text=f"{self.result_info['Name']} not found in any league.")
            return
        
        result_text += (f"{self.result_info['Name']} is ranked {self.result_info['Rank']} "
        f"with a score of {self.result_info['Score']} in the {self.result_info['League']} League.")
        
        if self.do_show_moveset.get():
            best_moveset = self.result_info['Best Moveset']
            result_text += (f"\nBest moveset: {best_moveset['Fast']}, {best_moveset['Charged1']}, "
                            f"{best_moveset['Charged2']}")

        if self.do_show_all_ranks.get():
            if self.result_info['Other Leagues']:
                other_leagues = self.result_info['Other Leagues']
                result_text += "\nOther leagues:"
                for league in other_leagues:
                    cur_rank = other_leagues[league][0][0]
                    cur_score = other_leagues[league][0][1]
                    result_text += f"\n{league} League: Rank #{cur_rank} (Score: {cur_score})"
                    # Add current league best moveset (if different from best league moveset)
                    if self.do_show_moveset.get() and other_leagues[league][1] != self.result_info['Best Moveset']:
                        result_text += (f" ({other_leagues[league][1]['Fast']}, "
                        f"{other_leagues[league][1]['Charged1']}, "
                        f"{other_leagues[league][1]['Charged2']})")
            else:
                result_text += f"\n{self.result_info['Name']} not found in any other leagues."

        self.result_label.config(text=result_text)


    def compare_rankings(self, query_name):
        best_rank = float('inf')
        best_score = float('-inf')
        best_league = None
        all_leagues = self.result_info['Other Leagues']
        for league in all_leagues.keys():
            cur_rank = all_leagues[league][0][0]
            cur_score = all_leagues[league][0][1]
            if cur_rank <= best_rank and cur_score > best_score:
                best_rank = cur_rank
                best_score = cur_score
                best_league = league

        self.result_info['Name'] = query_name.capitalize() # This is needed even if not found
        if best_league:
            best_moveset = all_leagues[best_league][1]
            self.result_info['Best Moveset'] = {}
            self.result_info['Best Moveset']['Fast'] = best_moveset['Fast']
            self.result_info['Best Moveset']['Charged1'] = best_moveset['Charged1']
            self.result_info['Best Moveset']['Charged2'] = best_moveset['Charged2']
            self.result_info['Rank'] = best_rank
            self.result_info['Score'] = best_score
            self.result_info['League'] = best_league.capitalize()
            other_leagues = all_leagues.copy()
            del other_leagues[best_league]
            other_leagues_sorted = dict(sorted(
                other_leagues.items(),
                key=lambda item: item[1][0][1],
                reverse=True
            ))
            self.result_info['Other Leagues'] = other_leagues_sorted
            self.result_info['Found'] = True
            return True
        else:
            self.result_info['Found'] = False
            return False


