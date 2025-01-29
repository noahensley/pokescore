
class UIInfo:
    def __init__(self, search_entry, result_label, suggestions_frame, do_show_all_ranks, show_all_ranks_checkbox):
        self.search_entry = search_entry
        self.result_label = result_label
        self.suggestions_frame = suggestions_frame
        self.do_show_all_ranks = do_show_all_ranks
        self.show_all_ranks_checkbox = show_all_ranks_checkbox
        self.suggestion_buttons = []  # List to track suggestion buttons

    def clear_suggestion_buttons(self):
        for button in self.suggestion_buttons:
            button.destroy()  # Remove the button from the UI
        self.suggestion_buttons.clear()  # Clear the list