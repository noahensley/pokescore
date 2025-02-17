import os.path
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import threading
import queue
from pytz import timezone

import UIInfo
from FileUtils import relative_path


def names_are_similar(n_longest, n_equalized, ch_error, len_error):
    """
    Check if two names are similar based on character and length differences.

    :param n_longest: The longer name.
    :param n_equalized: The equalized name for comparison.
    :param ch_error: The maximum allowable character difference.
    :param len_error: The maximum allowable length difference.
    :return: True if names are similar; False otherwise.
    """
    # Check for a length difference exceeding 3--excluding "()" tags
    if abs(len(n_longest.split(" (")[0]) - len(n_equalized.split(".")[0])) > len_error:
        return False
    
    # Check a character difference exceeding error
    diff = 0
    for i in range(0, len(n_longest)):
        if n_longest[i] != n_equalized[i]:
            diff += 1
        
        # Exit early
        if diff > ch_error:
            return False
        
        # Stops at spaces (modify this for edge cases)
        if n_longest[i] == " " or n_equalized[i] == " ":
            break
        
    return True
 

def equalize_names(supplied_name, data_name):
    """
    Equalize the lengths of two names by padding the shorter name with periods.

    :param supplied_name: The name provided by the user.
    :param data_name: The name from the dataset.
    :return: A tuple of the longer name and the equalized shorter name.
    """
    # Extract name data
    lowest_common_length, shortest_name, longest_name = (
        (len(data_name), supplied_name, data_name) if len(supplied_name) <= len(data_name) 
        else (len(supplied_name), data_name, supplied_name)
    )

    # Equalize the shorter name with the longer
    equalized_name = shortest_name
    for _ in range(0, lowest_common_length - len(shortest_name)):
        equalized_name += "."
        
    return longest_name, equalized_name


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


def suggest_similar_names(pokemon_name, data):
    """
    Suggest similar Pokémon names based on the supplied name.

    :param pokemon_name: The name of the Pokémon to search for.
    :param data: The dataset containing Pokémon names and rankings.
    :return: A list of up to 4 suggested Pokémon names.
    """
    suggestions = set() 
    ch_error = len(pokemon_name) * 0.5
    len_error = 3

    for league in data.values():
        for name in league["Pokemon"]:
            # Format both name boths to lower-case for comparison
            data_name = name.lower()
            supplied_name = pokemon_name.lower()

            # Equalize the longest and shortest names
            longest_name, equalized_name = equalize_names(supplied_name, data_name)
            shortest_name = equalized_name.split(".")[0]

            # Check if the longest name includes the shortest
            if longest_name.find(shortest_name) != -1:
                suggestions.add(name)

            # Check for similar names
            elif names_are_similar(longest_name, equalized_name, ch_error, len_error):
                suggestions.add(name)

    # Sort the suggestions prioritizing the initial of the supplied_name
    sorted_suggestions = sorted(suggestions, key=lambda x: (x[0].lower() != pokemon_name[0].lower(), x))
    return sorted_suggestions[:4]


def search_pokemon(data, ui_info):
    """
    Search for a Pokémon in the dataset and display its ranking or suggestions.

    :param data: The dataset containing Pokémon rankings.
    :param ui_info: The UIInfo object containing references to UI elements.
    """
    supplied_name = ui_info.search_entry.get().strip().lower()

    if not supplied_name:
        messagebox.showwarning("Input Error", "Please enter a Pokémon name.")
        return

    # Clear previous search results
    ui_info.result_label.config(text="")
    ui_info.clear_suggestion_buttons()
    ui_info.show_all_ranks_checkbox.grid_remove()  # Hide checkbox initially

    # Initialize classification variables
    best_score = float('-inf')
    best_rank = float('inf')
    best_league = None
    rank_scores = []  # Holds scores from all leagues

    # Search for the Pokémon in all leagues
    for league_name, league_data in data.items():
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
        if ui_info.do_show_all_ranks.get() and rank_scores:
            best_result_text += "\n\nOther leagues:\n" + "\n".join(rank_scores)

        ui_info.result_label.config(text=best_result_text)
        ui_info.show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)  # Show checkbox

    # If Pokémon was not found, suggest similar names
    else:
        suggestions = suggest_similar_names(supplied_name, data)
        if suggestions:
            display_suggestions(supplied_name, ui_info, suggestions, data)
        else:
            ui_info.result_label.config(text=f"{supplied_name.capitalize()} not found in any league.")

    # Focus and select all text in the search entry
    ui_info.search_entry.focus_set()
    ui_info.search_entry.selection_range(0, tk.END)


def display_suggestions(pokemon_name, ui_info, suggestions, data):
    """
    Display the suggestions as clickable buttons under the result label.

    :param pokemon_name: The name of the Pokémon searched by the user.
    :param suggestions: List of suggested Pokémon names.
    :param ui_info: The UIInfo object containing references to UI elements.
    :param data: The data dictionary with league information.
    """
    # Display the "not found" message
    ui_info.result_label.config(text=f"{pokemon_name.capitalize()} not found in any league.\nDid you mean one of these?")

    # Clear any previous suggestion buttons
    for button in ui_info.suggestion_buttons:
        button.destroy()
    ui_info.suggestion_buttons.clear()

    # Create buttons for each suggestion using grid
    for idx, name in enumerate(suggestions):
        button = ttk.Button(
            ui_info.result_label.master,  # Parent widget
            text=name,
            command=lambda n=name: ui_info.search_entry.delete(0, tk.END) or ui_info.search_entry.insert(0, n) or search_pokemon(data, ui_info)
        )
        button.grid(row=idx + 2, column=0, columnspan=3, pady=5, sticky=tk.EW)  # Adjust positioning
        ui_info.suggestion_buttons.append(button)  # Track the button


def on_suggestion_click(suggestion, ui_info, data):
    """
    Handle a click on a suggestion button.

    :param suggestion: The suggested Pokémon name.
    :param ui_info: The UIInfo object containing references to UI elements.
    :param data: The dataset containing Pokémon rankings.
    """
    ui_info.search_entry.delete(0, tk.END)
    ui_info.search_entry.insert(0, suggestion)
    search_pokemon(data, ui_info)


def initialize_interface(data):
    """
    Initialize the user interface for the Pokémon ranking search application.

    :param data: The dataset containing Pokémon rankings.
    """
    root = tk.Tk()
    root.title("Go Battle League Pokémon Ranking")
    root.geometry("600x500")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.grid_columnconfigure(0, weight=0)  # Left-aligned elements (labels, checkboxes, bottom_frame)
    frame.grid_columnconfigure(1, weight=1)  # Search entry should expand
    frame.grid_columnconfigure(2, weight=0)  # Right-side elements (buttons)
    frame.grid_rowconfigure(99, weight=1)  # Push bottom_frame to the bottom

    download_frame = ttk.Frame(frame)
    download_frame.grid(row=99, column=0, columnspan=2, sticky=tk.SW)

    search_label = ttk.Label(frame, text="Enter Pokémon Name:")
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    download_label = ttk.Label(frame, text="", foreground="blue")
    download_label.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)

    search_entry = ttk.Entry(frame, width=50)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
    search_entry.focus_set()

    search_button = ttk.Button(frame, text="Search", command=lambda: search_pokemon(data, ui_info))
    search_button.grid(row=0, column=2, padx=5, pady=5)

    result_label = ttk.Label(frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W)
    result_label.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    download_button = ttk.Button(download_frame, text="Download Assets")
    download_button.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)

    download_label = ttk.Label(download_frame, text="", foreground="blue")
    download_label.grid(row=0, column=1, padx=5, pady=1, sticky=tk.W)

    # Checkbox for displaying other league scores (initially hidden)
    do_show_all_ranks = tk.BooleanVar(value=False)
    show_all_ranks_checkbox = ttk.Checkbutton(frame, text="Show scores in other leagues", variable=do_show_all_ranks,
                                              command=lambda: search_pokemon(data, ui_info))
    show_all_ranks_checkbox.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
    show_all_ranks_checkbox.grid_remove()  # Hide initially

    # Frame for displaying suggestions
    suggestions_frame = ttk.Frame(frame)
    suggestions_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    ui_info = UIInfo.UIInfo(root, frame, download_frame, suggestions_frame,
                            search_label, search_button, search_entry, 
                            result_label, download_button, download_label,
                            do_show_all_ranks, show_all_ranks_checkbox)

    # Assign command after ui_info is created
    download_button.config(command=lambda: ui_info.download_assets())

    root.bind('<Return>', lambda event: search_pokemon(data, ui_info))
    root.mainloop()

