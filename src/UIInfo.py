import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from WebUtils import initialize_fetch_csv
import threading
import queue
import FileInfo
import FileUtils
import ClassifyUtils
import WebInfo
import re
from utils import core

class UIInfo(object):
    
    def __init__(self):

        self.csv_data = FileUtils.load_data()
        self.suggestion_buttons = []
        self.except_queue = queue.Queue(maxsize=3)
        self.formatted_query_info = {}
        self.local_iv_rankings = {}
        self.web_iv_info = WebInfo.WebInfo()
        self.previous_label_color = {}

        # ROOT
        self.root = tk.Tk()
        self.root.title("Go Battle League Pokémon Ranking")
        # ROW 
        self.root.rowconfigure(0, weight=0)  # interface_frame
        self.root.rowconfigure(1, weight=0)  # results_frame  
        self.root.rowconfigure(2, weight=0)  # suggestions_frame
        self.root.rowconfigure(3, weight=0)  # leagues_frame
        self.root.rowconfigure(4, weight=0)  # moveset_frame
        self.root.rowconfigure(5, weight=0)  # iv_frame
        self.root.rowconfigure(6, weight=1)  # download_frame (expandable)
        # COLUMN
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)  # Add columns 1 and 2
        self.root.columnconfigure(2, weight=0)  # to support columnspan=3
        
        # INIT
        # Styles
        ttk.Style().theme_use('clam')
        ttk.Style().configure('LargeBold.TLabel', font=('Arial', 12, 'bold'))
        ttk.Style().configure('Large.TLabel', font=('Arial', 12))
        ttk.Style().configure('Small.TLabel', font=('Arial', 10))
        ttk.Style().configure('Large.TCheckbutton', font=('Arial', 11))
        button_style = ttk.Style()
        button_style.configure('Large.TButton', font=('Arial', 12), foreground='black', background='#d9d9d9')
        button_style.map('Large.TButton', 
                         background=[('active', '#bfbfbf')])
        self.root.configure(bg=ttk.Style().lookup('TFrame', 'background')) # Match the root frame bg to the others
        # Frames
        self.interface_frame = ttk.Frame(self.root, padding="5")
        self.results_frame = ttk.Frame(self.root, padding="5")
        self.leagues_frame = ttk.Frame(self.root, padding="5")
        self.moveset_frame = ttk.Frame(self.root, padding="5")
        self.iv_frame = ttk.Frame(self.root, padding="5")
        self.suggestions_frame = ttk.Frame(self.root, padding="5")
        self.download_frame = ttk.Frame(self.root, padding="5")
        # Labels
        self.search_label = ttk.Label(self.interface_frame, text="Enter Pokémon Name:", style='LargeBold.TLabel')
        self.iv_label = ttk.Label(self.interface_frame, text="Enter IVs (e.g. 15,15,15):", foreground="dim gray", style='LargeBold.TLabel')
        self.iv_lookup_status_label = ttk.Label(self.interface_frame, text="", foreground="blue", style='Small.TLabel')
        self.result_header = ttk.Label(self.results_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                               style='LargeBold.TLabel')
        self.suggestions_header = ttk.Label(self.suggestions_frame, text="TEST", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                        style='Large.TLabel')
        self.leagues_header = ttk.Label(self.leagues_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                        style='LargeBold.TLabel')
        self.leagues_contents = ttk.Label(self.leagues_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                        style='Large.TLabel')
        self.moveset_header = ttk.Label(self.moveset_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                        style='LargeBold.TLabel')
        self.moveset_contents = ttk.Label(self.moveset_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                        style='Large.TLabel')
        self.iv_header = ttk.Label(self.iv_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                style='LargeBold.TLabel')
        self.iv_contents = ttk.Label(self.iv_frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W,
                                    style='Large.TLabel')  # light violet

        self.download_label = ttk.Label(self.download_frame, text="", foreground="blue", style='Large.TLabel')
        # Entries
        self.search_entry = ttk.Entry(self.interface_frame, width=25, font=('Arial', 12))
        self.iv_entry = ttk.Entry(self.interface_frame, width=10, font=('Arial', 12))
        # Buttons
        self.search_button = ttk.Button(self.interface_frame, text="Search", style='Large.TButton',
                                        command=lambda: self.query_csv_data())
        self.iv_lookup_button = ttk.Button(self.interface_frame, text="Lookup", style='Large.TButton',
                                           command=lambda: self.assign_web_info())
        self.download_assets_button = ttk.Button(self.download_frame, text="Download Assets", style='Large.TButton',
                                                 command=lambda: self.download_assets())
        # BooleanVar
        self.do_show_all_ranks = tk.BooleanVar(value=False) # Initially unchecked
        self.do_show_moveset = tk.BooleanVar(value=False) # Initially unchecked
        # Checkbuttons
        self.show_all_ranks_checkbox = ttk.Checkbutton(
                        self.interface_frame, 
                        text="Show scores in other leagues",
                        variable=self.do_show_all_ranks,
                        style='Large.TCheckbutton',
                        command=lambda: self.populate_results()
                    )
        
        self.show_moveset_checkbox = ttk.Checkbutton(
                        self.interface_frame,
                        text="Show moveset",
                        variable=self.do_show_moveset,
                        style='Large.TCheckbutton',
                        command=lambda: self.populate_results()
                    )
        
        # CONFIG
        # Frames
        self.interface_frame.grid_columnconfigure(0, weight=0)  # Left-aligned elements (labels, checkboxes, bottom_frame) (?)
        self.interface_frame.grid_columnconfigure(1, weight=1)  # Search entry (expanding)
        self.interface_frame.grid_rowconfigure(2, weight=0) # Checkbuttons
        self.interface_frame.grid_rowconfigure(3, weight=1)  # Push download_frame to the bottom
        self.results_frame.grid_columnconfigure(0, weight=1) # Frames stretch to the left
        self.results_frame.grid_rowconfigure(0, weight=0) # Result header
        self.results_frame.grid_rowconfigure(1, weight=0) # Result contents
        self.leagues_frame.grid_rowconfigure(0, weight=0) # Leagues header
        self.leagues_frame.grid_rowconfigure(1, weight=0) # Leagues contents
        self.moveset_frame.grid_rowconfigure(0, weight=0) # Moveset header
        self.moveset_frame.grid_rowconfigure(1, weight=0) # Moveset contents
        self.iv_frame.grid_rowconfigure(0, weight=0) # IV header
        self.iv_frame.grid_rowconfigure(1, weight=0) # IV contents
        self.suggestions_frame.grid_rowconfigure(0, weight=0) # Suggestion buttons
        self.suggestions_frame.grid_columnconfigure(0, weight=1)
        # Buttons
        self.iv_lookup_button.config(state=tk.DISABLED) # Disable before pokemon is searched
        # Entries
        self.iv_entry.config(state=tk.DISABLED) # Disable before pokemon is searched

        # GRID
        # Frames
        self.interface_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # results_frame is dynamically generated based on search
        self.download_frame.grid(row=6, column=0, columnspan=2, sticky=tk.SW)
        # Labels
        self.search_label.grid(row=0, column=0, padx=1, pady=0, sticky=tk.W)
        self.iv_label.grid(row=1, column=0, padx=1, pady=0, sticky=tk.W)
        self.iv_lookup_status_label.grid(row=1, column=1, columnspan=2, padx=100, sticky=tk.W)
        self.download_label.grid(row=0, column=1, padx=3, pady=0, sticky=tk.W) # row 0 of download_frame
        self.result_header.grid(row=0, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E)) # rows 0...10 of results_frame
        self.suggestions_header.grid(row=0, column=0, columnspan=3, pady=(0,3), sticky=(tk.W, tk.E)) # 0 top padding, 3 bottom
        self.leagues_header.grid(row=0, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        self.leagues_contents.grid(row=1, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        self.moveset_header.grid(row=0, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        self.moveset_contents.grid(row=1, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        self.iv_header.grid(row=0, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        self.iv_contents.grid(row=1, column=0, columnspan=3, pady=0, sticky=(tk.W, tk.E))
        # Entries
        self.search_entry.grid(row=0, column=1, padx=1, pady=4, sticky=tk.W)
        self.iv_entry.grid(row=1, column=1, padx=1, pady=4, sticky=tk.W)
        # Buttons
        self.search_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.iv_lookup_button.grid(row=1, column=2, padx=5, pady=0, sticky=tk.W)
        self.download_assets_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W) # row 0 of download_frame
        # Checkbuttons
        self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=2, pady=1, sticky=tk.W)
        self.show_moveset_checkbox.grid(row=2, column=1, columnspan=1, padx=50, pady=1, sticky=tk.W) # padx to not overlap
        
        self.search_entry.focus_set() # Focus the search bar      
        self.show_all_ranks_checkbox.grid_remove()  # Hide initially     
        self.show_moveset_checkbox.grid_remove() # Hide initially

        # Allow user to press 'Enter' to search
        self.root.bind('<Return>', self.handle_enter_press)
        self.root.bind('<Tab>', self.handle_tab_press)
        self.root.mainloop()


    def query_csv_data(self):
        """
        Search for a Pokémon in the CSV dataset and assign results to 'formatted_query_info' attribute.
        """
        supplied_name = self.search_entry.get().strip().lower()

        if not supplied_name:
            messagebox.showwarning("Input Error", "Please enter a Pokémon.")
            return

        # Clear previous search results
        self.result_header.config(text="")
        self.suggestions_header.config(text="")
        self.clear_suggestion_buttons()
        # Hide checkboxes each search
        self.show_all_ranks_checkbox.grid_remove()
        self.show_moveset_checkbox.grid_remove()

        # Initialize classification variables
        self.formatted_query_info['Other Leagues'] = {}
        csv_data = None

        # Search for the Pokémon in all leagues
        for league_name, league_data in self.csv_data.items():
            csv_data = league_data[league_data['Pokemon'].str.lower() == supplied_name]
            if not csv_data.empty:
                cur_index = csv_data.index[0]
                score = csv_data.at[cur_index, 'Score']
                rank = cur_index + 1 # Use row/index to calculate rank

                # Store current league information
                m_fast = csv_data.at[cur_index, 'Fast Move']
                m_charged1 = csv_data.at[cur_index, 'Charged Move 1']
                m_charged2 = csv_data.at[cur_index, 'Charged Move 2']
                self.formatted_query_info['Other Leagues'][league_name.capitalize()] = (
                    (rank, score), 
                    {'Fast': m_fast, 'Charged1': m_charged1, 'Charged2': m_charged2}
                )

        # If Pokémon was found, determine best league and remove it from 'Other Leagues'
        if self.compare_rankings(supplied_name):       
            # Display 'other leagues' checkbox
            self.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W)
            # Display 'moveset' checkbox
            self.show_moveset_checkbox.grid(row=2, column=1, columnspan=1, pady=5, sticky=tk.W)
        
        self.local_iv_rankings = {} # Reset IV info on new searchs
        # Display results or display suggestions
        self.populate_results()

        # Focus and select all text in the search entry
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)

        # Reset IV label/entry if needed
        self.iv_lookup_status_label.config(text="") # Clear Success code
        self.iv_entry.delete(0, tk.END) # Clear IV input on new search


    def assign_web_info(self):
        """
        Populates the 'web_iv_info' attribute, performs web query, and localizes the results
        to 'local_iv_rankings'.
        """
        name = self.search_entry.get().strip().lower()
        ivs = self.iv_entry.get().strip().lower()
        name = self.remove_shadow_label(name)
        
        match = re.search(core.iv_pattern, ivs)

        if not match:
            self.iv_lookup_status_label.config(text="Invalid IV Format.", foreground="red2")
            self.iv_entry.focus_set()
            self.iv_entry.selection_range(0, tk.END)
            return

        if name == "":
            self.iv_lookup_status_label.config(text="Please enter a Pokemon name.", foreground="red2")
            self.search_entry.focus_set()
            return

        ivs = [item.strip() for item in ivs.split(",")]

        if self.web_iv_info != None:
            if ivs == [self.web_iv_info.attack_iv, self.web_iv_info.defense_iv, self.web_iv_info.stamina_iv] and name == self.web_iv_info.pokemon_name:
                self.iv_lookup_status_label.config(text="IVs already displayed.", foreground="blue")
                return

        self.web_iv_info.pokemon_name = self.capitalize_form_label(name)
        self.web_iv_info.attack_iv = ivs[0]
        self.web_iv_info.defense_iv = ivs[1]
        self.web_iv_info.stamina_iv = ivs[2]

        if self.web_iv_info.fetch_ivs() == False:
            self.iv_lookup_status_label.config(text="Could not find Pokemon.", foreground="red2")
            self.search_entry.focus_set()
            self.iv_entry.selection_range(0, tk.END)
            return
        
        self.iv_lookup_status_label.config(text="Success", foreground="blue")
        # Copy the results to the UIInfo in ascending order
        self.local_iv_rankings = dict(sorted(self.web_iv_info.ranks.items(), key=lambda item: int(item[1])))
        self.populate_results()

        # Highlight IV entry selection
        self.iv_entry.focus_set()
        self.iv_entry.selection_range(0, tk.END)


    def display_suggestions(self, suggestions):
        """
        Displays suggested Pokémon as clickable buttons under the result label.  This function is used when no 
        Pokémon could be found matching the user's query.

        :param suggestions: List of suggested Pokémon names genereated by ClassifyUtils.suggest_similar_names.
        """
        # Clear any previous suggestion buttons
        self.suggestion_buttons.clear()

        # Display the "not found" message
        self.result_header.config(text=f"{self.formatted_query_info['Name']} not found in any League.")
        self.suggestions_header.config(text="Did you mean one of these?")

        # Create buttons for each suggestion using grid
        for idx, name in enumerate(suggestions):
            button = ttk.Button(
                self.suggestions_frame,  # Parent widget
                text=name,
                command=lambda n=name: self.search_entry.delete(0, tk.END) or self.search_entry.insert(0, n) or self.query_csv_data()
            )
            button.grid(row=idx + 1, column=0, columnspan=3, pady=5, padx=10, sticky=tk.EW)  # +1 to avoid row 0 conflict (suggestion frame)
            self.suggestion_buttons.append(button)  # Track the button


    def clear_suggestion_buttons(self):
        """
        Wipes the suggestion buttons from the user interface when no longer needed and updates
        'suggestion_buttons' list accordingly.
        """
        for button in self.suggestion_buttons:
            button.destroy()  # Remove the button from the UI
        self.suggestion_buttons.clear()  # Clear the list


    def disable_ui(self):
        """
        Disables all interactable elements of the user interface.
        """
        self.search_entry.config(state=tk.DISABLED)
        self.iv_entry.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        self.iv_lookup_button.config(state=tk.DISABLED)
        for button in self.suggestion_buttons:
            button.config(state=tk.DISABLED)
        self.download_assets_button.config(state=tk.DISABLED)
        # Change text visuals
        for inner_frame in self.root.children:
            frame = self.root.children[inner_frame]
            for frame_child in frame.children:
                child = frame.children[frame_child]
                if child is self.download_label:
                    continue # Keep the status code color
                if isinstance(child, (tk.Label, ttk.Label)):
                    if child.cget("text"):
                        prev_color = child.cget("foreground")
                        self.previous_label_color[child] = prev_color # Store current color
                        child.config(foreground="dim grey")

        self.disable_close() # Disable close button


    def reenable_ui(self):
        """
        Re-enables all interactable elements of the user interface.
        """
        self.search_entry.config(state=tk.NORMAL)
        self.iv_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.iv_lookup_button.config(state=tk.NORMAL)
        for button in self.suggestion_buttons:
            button.config(state=tk.NORMAL)
        self.download_assets_button.config(state=tk.NORMAL)
        # Restore text visuals
        for inner_frame in self.root.children:
            frame = self.root.children[inner_frame]
            for frame_child in frame.children:
                child = frame.children[frame_child]
                if child is self.download_label:
                    continue # This color never changed
                if isinstance(child, (tk.Label, ttk.Label)):
                    if child.cget("text"):
                        color = self.previous_label_color[child]
                        child.config(foreground=color)
        self.reenable_close()  # Restore close button


    def disable_close(self):
        """
        Disables the window's close (X) button.
        """
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # Ignore close button presses


    def reenable_close(self):
        """
        Re-enable the window's close (X) button
        """
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)  # Restore normal behavior


    def download_assets(self):
        """
        Disables the user interface and executes 'perform_download' in a thread.
        """
        def perform_download():
            """
            Performs the CSV file download and displays the status on the user interface.
            """
            try:
                file_info = FileInfo.FileInfo()
                file_info.make_data_backup()

                initialize_fetch_csv(self.except_queue, file_info)

                # Wait for threads to finish
                while not self.except_queue.full():
                    pass

                # Ensures threads did not fail
                while not self.except_queue.empty():
                    ecode = self.except_queue.get()
                    if ecode != None:
                        self.download_label.config(text=f"Download failed.", foreground="red2")
                        file_info.restore_data_backup()
                        return

                # Ensures required files are present
                if not file_info.downloads_successful():
                    self.download_label.config(text=f"Download failed.", foreground="red2")
                    file_info.restore_data_backup()
                    return

                self.csv_data = FileUtils.load_data()
                self.download_label.config(text=f"Download complete.")
                file_info.discard_backup()

            except Exception as e:
                self.download_label.config(text=f"Error: {e}", foreground="red2")
            finally:
                self.reenable_ui()

        self.download_label.config(text=f"Downloading assets...", foreground="blue")
        self.disable_ui()

        fetch_thread = threading.Thread(target=perform_download)
        fetch_thread.start()


    def populate_results(self):
        """
        Dynamically populates the information frames of the user interface.
        """
        self.populate_results_header()
        self.populate_leagues_result()
        self.populate_moveset_result()
        self.populate_iv_result()
        self.manage_frame_visibility()


    def manage_frame_visibility(self):
        """
        Shows or hides frames based on whether they have content.
        """
        # Check if results frame has any content
        for frame in self.root.children:
            cur_frame = self.root.children[frame]
            if cur_frame is self.interface_frame or cur_frame is self.download_frame:
                continue
            self.root.children[frame].grid_remove() # Initially hide all frames

        cur_row = 1
        for child_name in self.root.children:
            frame = self.root.children[child_name]
            
            # Skip the download frame
            if frame is self.download_frame or frame is self.interface_frame:
                continue
                
            if isinstance(frame, (tk.Frame, ttk.Frame)):
                has_content = False
                
                # Special handling for suggestions frame - check if it has buttons
                if frame is self.suggestions_frame:
                    has_content = len(self.suggestion_buttons) > 0
                    # Also check if the header has text
                    if not has_content:
                        try:
                            header_text = self.suggestions_header.cget("text")
                            has_content = header_text and header_text.strip()
                        except tk.TclError:
                            pass
                else:
                    # Check the frame's children for labels with text
                    for child_widget_name in frame.children:
                        child_widget = frame.children[child_widget_name]
                        
                        # Only check labels for text content
                        if isinstance(child_widget, (tk.Label, ttk.Label)):
                            try:
                                text = child_widget.cget("text")
                                if text and text.strip():  # Not empty or just whitespace
                                    has_content = True
                                    break
                            except tk.TclError:
                                pass
                
                # Show or hide the frame based on content
                if has_content:
                    frame.grid(row=cur_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                    cur_row += 1
                else:
                    frame.grid_remove()
                    

    def populate_results_header(self):
        """
        Populates the result label with the main query information.  This main information is the queried Pokémon's
        top ranked league and the Pokémon's score for that league.
        """
        result_header_text = ""
        if not self.formatted_query_info:
            self.result_header.config(text=result_header_text)
            return
        
        if not self.formatted_query_info['Found']:
            self.do_show_all_ranks.set(False)
            self.do_show_moveset.set(False)
            self.disable_iv_lookup()
            suggestions = ClassifyUtils.suggest_similar_names(self.formatted_query_info['Name'], self.csv_data)
            if suggestions:
                self.display_suggestions(suggestions)
            else:
                self.result_header.config(text=f"{self.formatted_query_info['Name']} not found in any league.")
            return
        else:
            self.enable_iv_lookup()
        
        result_header_text += (f"{self.formatted_query_info['Name']} is ranked {self.formatted_query_info['Rank']} "
        f"with a score of {self.formatted_query_info['Score']} in the {self.formatted_query_info['League']} League.")
        self.result_header.config(text=result_header_text)


    def populate_leagues_result(self):
        """
        Populates both the 'other leagues' label and information frame.  The label will signal if the queried
        Pokémon was found in any other leagues or not.
        """
        result_leagues_text = ""
        if self.do_show_all_ranks.get():
            if self.formatted_query_info['Other Leagues']:
                self.leagues_header.config(text="Other Leagues:")
                other_leagues = self.formatted_query_info['Other Leagues']
                num_leagues = len(other_leagues)
                for idx, league in enumerate(other_leagues):
                    cur_rank = other_leagues[league][0][0]
                    cur_score = other_leagues[league][0][1]
                    result_leagues_text += f"{league} League: Rank #{cur_rank} (Score: {cur_score})"
                    if idx < num_leagues:
                        result_leagues_text += "\n" # Ensure no trailing newline
                    # Add current league best moveset (if different from best league moveset)
                    if self.do_show_moveset.get():
                        alt_moveset = other_leagues[league][1].values()
                        shown_moveset = self.formatted_query_info['Best Moveset'].values()
                        if sorted(alt_moveset) != sorted(shown_moveset):
                            different_moves = list(set(alt_moveset) - set(shown_moveset))
                            result_leagues_text += (" (Diff: ")
                            for idx, move in enumerate(different_moves):
                                result_leagues_text += (f"*{move}")
                                if idx < len(different_moves) - 1:
                                    result_leagues_text += ", "
                                else:
                                    result_leagues_text += ")\n"



            else:
                self.leagues_header.config(text=f"{self.formatted_query_info['Name']} not found in any other leagues.")

        else:
            # DO NOT show ranks
            self.leagues_header.config(text="")
            self.leagues_contents.config(text="")

        self.leagues_contents.config(text=result_leagues_text)


    def populate_moveset_result(self):
        """
        Populates both the 'moveset' label and information frame.  The label is merely a header where the
        information frame will contain the best moveset for the queried Pokémon.
        """
        if self.do_show_moveset.get():
            self.moveset_header.config(text="Best Moveset:")
            best_moveset = self.formatted_query_info['Best Moveset']
            result_moveset_text = (f"{best_moveset['Fast']}, {best_moveset['Charged1']}, "
                            f"{best_moveset['Charged2']}")

            self.moveset_contents.config(text=result_moveset_text)
        
        else:
            # DO NOT show moveset
            self.moveset_header.config(text="")
            self.moveset_contents.config(text="")


    def populate_iv_result(self):
        """
        Populates both the 'IV Rankings' label and information frame.  The label is merely a header where the
        information frame will contain the rankings of the IV spread for the queried Pokémon in each applicable
        league.
        """
        result_iv_text = ""
        if self.local_iv_rankings:
            self.iv_header.config(text="IV Rankings:")
            num_leagues = len(self.local_iv_rankings.keys())
            for idx, league in enumerate(self.local_iv_rankings):
                result_iv_text += f"{league}: {self.web_iv_info.stringify_ivs()} => #{self.local_iv_rankings[league]}"
                if idx < num_leagues - 1:
                    result_iv_text += "\n" # Ensure no trailing newline

            self.iv_contents.config(text=result_iv_text)
        
        else:
            # DO NOT show IV rankings
            self.iv_header.config(text="")
            self.iv_contents.config(text="")


    def compare_rankings(self, query_name):
        """
        Searches and compares the rank and score of a Pokémon in each applicable league.  If a best league is found, the
        function updates 'formatted_query_info' with the corresponding rank, score, and moveset data.  Indicates whether
        a league was found for the queried Pokémon.

        :param query_name: The user-supplied text grabbed from the search entry.
        """
        best_rank = float('inf')
        best_score = float('-inf')
        best_league = None
        all_leagues = self.formatted_query_info['Other Leagues']
        for league in all_leagues.keys():
            cur_rank = all_leagues[league][0][0]
            cur_score = all_leagues[league][0][1]
            if cur_rank < best_rank:
                best_rank = cur_rank
                best_score = cur_score
                best_league = league
            elif cur_rank == best_rank and cur_score > best_score: # When ranks tie, score takes precedence
                best_rank = cur_rank
                best_score = cur_score
                best_league = league

        query_name = self.capitalize_form_label(query_name)
        self.formatted_query_info['Name'] = query_name # This is needed even if not found (best_league == None)
        if best_league:
            best_moveset = all_leagues[best_league][1]
            self.formatted_query_info['Best Moveset'] = {}
            self.formatted_query_info['Best Moveset']['Fast'] = best_moveset['Fast']
            self.formatted_query_info['Best Moveset']['Charged1'] = best_moveset['Charged1']
            self.formatted_query_info['Best Moveset']['Charged2'] = best_moveset['Charged2']
            self.formatted_query_info['Rank'] = best_rank
            self.formatted_query_info['Score'] = best_score
            self.formatted_query_info['League'] = best_league.capitalize()
            other_leagues = all_leagues.copy()
            del other_leagues[best_league]
            # Sort other leagues by descending rank
            other_leagues_sorted = dict(sorted(
                other_leagues.items(),
                key=lambda item: item[1][0][0],
            ))
            self.formatted_query_info['Other Leagues'] = other_leagues_sorted
            self.formatted_query_info['Found'] = True
            return True
        else:
            self.formatted_query_info['Found'] = False
            return False
        

    def handle_enter_press(self, event):
        """
        Allows the user to press 'Enter' to perform a search or an IV lookup.

        :param event: The target event.
        """
        focused = event.widget.focus_get()
        if focused == self.search_entry:
            self.query_csv_data()
        elif focused == self.iv_entry:
            self.assign_web_info()


    def handle_tab_press(self, event):
        """
        Allows the user to cycle between the search and IV lookup entries using 'Tab'.  Returns "break" to 
        override the default tkinter 'Tab' behavior.

        :param event: The target event.
        """
        focused = event.widget.focus_get()
        if focused == self.search_entry:
            if 'disabled' not in self.iv_entry.state():
                self.iv_entry.focus_set()
                self.iv_entry.selection_range(0, tk.END)
        elif focused == self.iv_entry:
            self.search_entry.focus_set()
            self.search_entry.selection_range(0, tk.END)
        else:
            self.search_entry.focus_set()
            self.search_entry.selection_range(0, tk.END)
        return "break"


    def remove_shadow_label(self, name):
        """
        Removes the '(Shadow)' label from a name, if present.  Necessary because the '(Shadow)' label
        is not used for an IV lookup.

        :param name: The Pokémon name with or without the '(Shadow)' label.
        """
        if type(name) != str:
            raise RuntimeError("Input name must be a string.")
        
        lower_name = name.lower()
        index = lower_name.find(" (shadow)")
        if index != -1:
            return name[:index]
        
        return name
    

    def capitalize_form_label(self, name):
        """
        Checks the supplied name for a form label and properly capitalizes it AND the Pokémon name
        (including hyphenated names).  If there is no form label, only the capitalized name is 
        returned.

        :param name: The name to properly capitalize.
        """
        # Always capitalize first letter
        name = name.capitalize()

        indices = []
        i_hyphen = 0
        tag_start = 0
        tag_end = 0
        i_compound = 0
        # Search for hyphen can be done before tag, because no form labels
        # include hyphens--I think.
        while True:
            i_hyphen = name.find("-", i_hyphen, len(name)-1)
            if i_hyphen == -1:
                break
            i_hyphen += 1
            if i_hyphen < len(name):
                indices.append(i_hyphen)

        while True:
            tag_start = name.find("(", tag_start, len(name)-1)
            if tag_start == -1:
                break
            tag_start += 1
            if tag_start < len(name):
                indices.append(tag_start)
            tag_end = name.find(")", tag_start)

            i_compound = tag_start
            while i_compound != -1:
                i_compound = name.find(" ", i_compound, tag_end)
                if i_compound != -1 and i_compound + 1 < len(name):
                    i_compound += 1
                    indices.append(i_compound)

        if len(indices) == 0:
            return name

        list_copy = list(name)
        for i in indices:
            list_copy[i] = list_copy[i].upper()

        return "".join(list_copy)
    
    
    def disable_iv_lookup(self):
        self.iv_label.config(foreground="dim gray")
        self.iv_entry.config(state=tk.DISABLED)
        self.iv_lookup_button.config(state=tk.DISABLED)
        #optional error code


    def enable_iv_lookup(self):
        self.iv_label.config(foreground="black") #Un-gray the text
        self.iv_entry.config(state=tk.NORMAL)
        self.iv_lookup_button.config(state=tk.NORMAL)
        self.iv_lookup_status_label.config(text="") # Clear Success code
        self.iv_entry.delete(0, tk.END) # Clear IV input on new search

