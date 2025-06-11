

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