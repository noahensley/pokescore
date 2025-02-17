
class UIInfo (object):
    def __init__(self, root, frame, download_frame, suggestions_frame,
                 search_label, search_button, search_entry, result_label, 
                 download_button, download_label, 
                 do_show_all_ranks, show_all_ranks_checkbox):
        
        self.root = root
        self.frame = frame
        self.download_frame = download_frame
        self.search_label = search_label
        self.search_button = search_button
        self.search_entry = search_entry
        self.result_label = result_label
        self.suggestions_frame = suggestions_frame
        self.do_show_all_ranks = do_show_all_ranks
        self.show_all_ranks_checkbox = show_all_ranks_checkbox
        self.suggestion_buttons = []  # List to track suggestion buttons
        self.download_assets_button = download_button
        self.download_label = download_label

    def clear_suggestion_buttons(self):
        for button in self.suggestion_buttons:
            button.destroy()  # Remove the button from the UI
        self.suggestion_buttons.clear()  # Clear the list