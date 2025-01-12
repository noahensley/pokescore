import os.path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import UIInfo

def names_are_similar(name1, name2, error):
    if abs(len(name1.split(" (")[0]) - len(name2.split(" (")[0])) > 3:
        return False
    
    diff = 0
    for i in range(0,len(name1)):
        if name1[i] is not name2[i]:
            diff += 1
    
        if diff > error:
            return False
        
        if name1[i] == " " or name2[i] == " ":
            break
        
    return True
 

def equalize_names(supplied_name, data_name):
    # Equalize length of input and data names
    lowest_common_length, shortest_name, longest_name = (
        (len(data_name), supplied_name, data_name) if len(supplied_name) <= len(data_name) 
        else (len(supplied_name), data_name, supplied_name)
    )

    equalized_name = shortest_name
    # Equalize length of input-/data-name
    for i in range(0, lowest_common_length - len(shortest_name)):
        equalized_name += "."

    return longest_name, equalized_name


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

    # Estimate input error based on input length
    error = len(pokemon_name) * 0.5

    for league in data.values():
        for name in league["Pokemon"]:
            # Convert both names to lower-case for comparison
            data_name = name.lower()
            supplied_name = pokemon_name.lower()
            
            # Equalize names using lowest common length
            longest_name, equalized_name = equalize_names(supplied_name, data_name)

            # Extract shortest name from equalized
            # (equalized name is formatted 'name...')
            shortest_name = equalized_name.split(".")[0]

            if longest_name.find(shortest_name) != -1:
                suggestions.add(name)

            elif names_are_similar(longest_name, equalized_name, error):
                suggestions.add(name)

    # Sort suggestions alphabetically starting with the first letter of the supplied name
    sorted_suggestions = sorted(suggestions, key=lambda x: (x[0].lower() != pokemon_name[0].lower(), x))

    # Limit to 4 suggestions
    return sorted_suggestions[:4]


# Function to search for a Pokemon's best league and ranking
def search_pokemon(data, ui_info):
    supplied_name = ui_info.search_entry.get().strip().lower()
    if not supplied_name:
        messagebox.showwarning("Input Error", "Please enter a Pokemon name.")
        return

    best_score = float('-inf')
    best_rank = None
    best_league = None

    for league_name, league_data in data.items():
        result = league_data[league_data['Pokemon'].str.lower() == supplied_name]
        if not result.empty:
            score = result.at[result.index[0], 'Score']  # Access the Score value without using iloc
            rank = result.index[0] + 1  # Adjusting for 0-based indexing
            if score > best_score:  # Higher scores indicate better ranking
                best_rank = rank
                best_score = score
                best_league = league_name

    if best_league is None:
        suggestions = suggest_similar_names(supplied_name, data)
        if suggestions:
            suggestion_text = "Did you mean: " + ", ".join(suggestions) + "?"
            ui_info.result_label.config(text=f"{supplied_name.capitalize()} not found in any league.\n{suggestion_text}")
        else:
            ui_info.result_label.config(text=f"{supplied_name.capitalize()} not found in any league.")
    else:
        ui_info.result_label.config(text=f"{supplied_name.capitalize()} is ranked #{best_rank} "                                    
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
