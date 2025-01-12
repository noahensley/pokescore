import os.path
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import UIInfo


def names_are_similar(n_longest, n_equalized, ch_error, len_error):
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
    try:
        # Import .csv rankings from pvpoke.com
        current_dir = os.path.dirname(os.path.abspath(__file__))
        great_league = pd.read_csv(os.path.join(current_dir, '../data/cp1500_all_overall_rankings.csv'))
        ultra_league = pd.read_csv(os.path.join(current_dir, '../data/cp2500_all_overall_rankings.csv'))
        master_league = pd.read_csv(os.path.join(current_dir, '../data/cp10000_all_overall_rankings.csv'))

        return {
            'great': great_league,
            'ultra': ultra_league,
            'master': master_league
        }
    except FileNotFoundError as e:
        messagebox.showerror("File Not Found", f"Could not find file: {e.filename}")
        exit()


def suggest_similar_names(pokemon_name, data):
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
    supplied_name = ui_info.search_entry.get().strip().lower()

    # Clear the suggestion label before performing a new search
    ui_info.result_label.config(text="")
    ui_info.clear_suggestion_buttons()

    if not supplied_name:
        messagebox.showwarning("Input Error", "Please enter a Pokémon name.")
        return
    
    # Initialize classification variables
    best_score = float('-inf')
    best_rank = None
    best_league = None

    # Classify the supplied name of the Pokemon
    for league_name, league_data in data.items():
        result = league_data[league_data['Pokemon'].str.lower() == supplied_name]
        if not result.empty:
            score = result.at[result.index[0], 'Score']
            rank = result.index[0] + 1
            if score > best_score:
                best_rank = rank
                best_score = score
                best_league = league_name
    
    # Generate suggestions if supplied name is not found
    if best_league is None:
        suggestions = suggest_similar_names(supplied_name, data)
        if suggestions:
            display_suggestions(supplied_name, ui_info, suggestions, data)
        else:
            ui_info.result_label.config(text=f"{supplied_name.capitalize()} not found in any league.")

    # Display the classification of the Pokemon with the supplied name
    else:
        ui_info.result_label.config(text=f"{supplied_name.capitalize()} is ranked #{best_rank} "
                                         f"with a score of {best_score} in the {best_league.capitalize()} League.")
        
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
    ui_info.search_entry.delete(0, tk.END)
    ui_info.search_entry.insert(0, suggestion)
    search_pokemon(data, ui_info)


def initialize_interface(data):
    root = tk.Tk()
    root.title("Go Battle League Pokémon Ranking")
    root.geometry("600x500")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.columnconfigure(1, weight=1)

    search_label = ttk.Label(frame, text="Enter Pokémon Name:")
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    search_entry = ttk.Entry(frame, width=50)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
    search_entry.focus_set()

    search_button = ttk.Button(frame, text="Search", command=lambda: search_pokemon(data, ui_info))
    search_button.grid(row=0, column=2, padx=5, pady=5)

    result_label = ttk.Label(frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W)
    result_label.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    suggestions_frame = ttk.Frame(frame)
    suggestions_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    ui_info = UIInfo.UIInfo(search_entry, result_label, suggestions_frame)

    root.bind('<Return>', lambda event: search_pokemon(data, ui_info))
    root.mainloop()
