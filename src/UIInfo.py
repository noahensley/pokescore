

class UIInfo:
    def __init__(self, search_entry, result_label, suggestions_frame):
        self.search_entry = search_entry
        self.result_label = result_label
        self.suggestions_frame = suggestions_frame
        self.suggestion_buttons = []  # List to track suggestion buttons

    def clear_suggestion_buttons(self):
        for button in self.suggestion_buttons:
            button.destroy()  # Remove the button from the UI
        self.suggestion_buttons.clear()  # Clear the list