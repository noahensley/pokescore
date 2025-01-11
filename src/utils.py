import os.path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd

import UIInfo

# Load the CSV data
def load_data():
    try:
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


# Function to provide suggestions for similar Pokemon names
def suggest_similar_names(pokemon_name, data):
    suggestions = set()
    for league_data in data.values():
        similar_names = league_data[league_data['Pokemon'].str.lower().str.contains(pokemon_name[:3], na=False, regex=False)]
        suggestions.update(similar_names['Pokemon'].tolist())
    return list(suggestions)


# Function to search for a Pokemon's best league and ranking
def search_pokemon(data, ui_info):
    pokemon_name = ui_info.search_entry.get().strip().lower()
    if not pokemon_name:
        messagebox.showwarning("Input Error", "Please enter a Pokemon name.")
        return

    best_score = float('-inf')
    best_rank = None
    best_league = None

    for league_name, league_data in data.items():
        result = league_data[league_data['Pokemon'].str.lower() == pokemon_name]
        if not result.empty:
            score = result.at[result.index[0], 'Score']  # Access the Score value without using iloc
            rank = result.index[0] + 1  # Adjusting for 0-based indexing
            if score > best_score:  # Higher scores indicate better ranking
                best_rank = rank
                best_score = score
                best_league = league_name

    if best_league is None:
        suggestions = suggest_similar_names(pokemon_name, data)
        if suggestions:
            suggestion_text = "Did you mean: " + ", ".join(suggestions) + "?"
            ui_info.result_label.config(text=f"{pokemon_name.capitalize()} not found in any league.\n{suggestion_text}")
        else:
            ui_info.result_label.config(text=f"{pokemon_name.capitalize()} not found in any league.")
    else:
        ui_info.result_label.config(text=f"{pokemon_name.capitalize()} is ranked #{best_rank} "                                    
                                    f"with a score of {best_score} in the {best_league.capitalize()} League.")


# Initialize UI elements
def initialize_interface(data):
    # Create the main window
    root = tk.Tk()
    root.title("Go Battle League Pokemon Ranking")
    root.geometry("600x400")

    # Configure the grid to expand dynamically
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Create UI elements
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    frame.columnconfigure(1, weight=1)

    search_label = ttk.Label(frame, text="Enter Pokemon Name:")
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    search_entry = ttk.Entry(frame, width=50)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
    search_entry.focus_set()  # Automatically focus the search entry

    search_button = ttk.Button(frame, text="Search", command=lambda: search_pokemon(data, ui_info))
    search_button.grid(row=0, column=2, padx=5, pady=5)

    result_label = ttk.Label(frame, text="", wraplength=500, justify=tk.LEFT, anchor=tk.W)
    result_label.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

    ui_info = UIInfo.UIInfo(search_entry, result_label)

    # Bind the Enter key to trigger the search
    root.bind('<Return>', lambda event: search_pokemon(data, ui_info))

    # Start the main loop
    root.mainloop()
