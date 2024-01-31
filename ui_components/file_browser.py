from tkinter import filedialog
from pathlib import Path
from typing import Any


class FileBrowser:
    def __init__(self, main_ui: Any):
        self.main_ui = main_ui

    def browse_file(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.main_ui.mod_directory_var.set(directory_path)
            self.main_ui.mod_directory_combobox.set(directory_path)

            if directory_path not in self.main_ui.directory_paths_list:
                self.main_ui.directory_paths_list.append(directory_path)
                self.main_ui.mod_directory_combobox.configure(
                    values=self.main_ui.directory_paths_list
                )

            if directory_path == "":
                quit()

            self.submit_mod_directory()

    def submit_mod_directory(self):
        mod_directory = Path(self.main_ui.mod_directory_var.get())
        if mod_directory.exists():
            self.main_ui.destroy_song_widgets()
            self.main_ui.create_song_widgets()
