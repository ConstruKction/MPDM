from pathlib import Path
from tkinter import filedialog

import customtkinter

from mod_pv_db_scanner import ModPvDbScanner


class MainUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('MPDM')
        self.geometry(self.set_window_size())
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.directory_paths_list = []  # For ComboBox dropdown memory

        # Path Entry and Browse Button
        self.mod_directory_var = customtkinter.StringVar()
        self.mod_directory_label = customtkinter.CTkLabel(self, text='Mod Directory Path', fg_color='transparent')
        self.mod_directory_combobox = customtkinter.CTkComboBox(self, variable=self.mod_directory_var, values=[],
                                                                command=lambda event=None:
                                                                self.combobox_path_selected())
        self.browse_button = customtkinter.CTkButton(self, text='Browse', command=self.browse_file)

        # Song Checklist
        self.songs_checkbox_frame = customtkinter.CTkScrollableFrame(master=self)

        # Grid Layout
        self.mod_directory_label.grid(row=0, column=0, padx=20, pady=5, sticky='ew')
        self.mod_directory_combobox.grid(row=1, column=0, padx=20, sticky='ew')
        self.browse_button.grid(row=2, column=0, padx=20, pady=5, sticky='ew')
        self.songs_checkbox_frame.grid(row=3, column=0, padx=20, pady=20, sticky='nsew')

    def set_window_size(self) -> str:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width_percent = 40
        height_percent = 70
        width = (screen_width * width_percent) // 100
        height = (screen_height * height_percent) // 100

        return f'{width}x{height}+{screen_width // 2 - width // 2}+{screen_height // 2 - height // 2}'

    def combobox_path_selected(self):
        selected_path = self.mod_directory_combobox.get()
        if selected_path:
            self.mod_directory_var.set(selected_path)
            self.submit_mod_directory()

    def browse_file(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.mod_directory_var.set(directory_path)
            self.mod_directory_combobox.set(directory_path)

            if directory_path not in self.directory_paths_list:
                self.directory_paths_list.append(directory_path)
                self.mod_directory_combobox.configure(values=self.directory_paths_list)

            self.submit_mod_directory()

    def update_song_list(self):
        self.clear_song_list()
        mod_pv_db_scanner = ModPvDbScanner(self.mod_directory_var.get())
        songs = mod_pv_db_scanner.get_all_songs()

        for index, song in enumerate(songs):
            checkbox = customtkinter.CTkCheckBox(master=self.songs_checkbox_frame, text=f'{song[0]} - {song[1]}')
            checkbox.grid(row=index, column=0, pady=(0, 10), sticky='w')

    def clear_song_list(self):
        for widget in self.songs_checkbox_frame.winfo_children():
            widget.destroy()

    def submit_mod_directory(self):
        mod_directory = Path(self.mod_directory_var.get())
        if mod_directory.exists():
            self.update_song_list()
