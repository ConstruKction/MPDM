from pathlib import Path
from tkinter import filedialog

import customtkinter

from mod_pv_db_scanner import ModPvDbScanner
from ui_components.song_widget import SongWidget
from ui_components.progress_bar import ProgressBar


class MainUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("MPDM")
        self.geometry(self.set_window_size())
        self.grid_columnconfigure(0, weight=1)
        self.directory_paths_list = []  # For ComboBox dropdown memory
        self.song_widgets = []
        self.song_pack_filter_optionmenu_populated = False

        # Path ComboBox
        self.mod_directory_var = customtkinter.StringVar()
        self.mod_directory_combobox = customtkinter.CTkComboBox(
            self,
            variable=self.mod_directory_var,
            values=[],
            command=lambda event=None: self.combobox_path_selected(),
        )

        # Song Search Bar
        self.search_bar_var = customtkinter.StringVar()
        self.search_bar_var.trace_variable("w", self.update_scrollable_song_frame)
        self.search_bar = customtkinter.CTkEntry(self, placeholder_text="Search", textvariable=self.search_bar_var)
        self.search_bar.bind("<KeyRelease>", self.dynamic_search)

        # Browse Button
        self.browse_button = customtkinter.CTkButton(
            self, text="Browse", command=self.browse_file
        )

        # Song Pack Filter OptionMenu
        self.song_pack_filter_var = customtkinter.StringVar()
        self.song_pack_filter_var.set("All")
        self.song_pack_filter_optionmenu = customtkinter.CTkOptionMenu(
            self, variable=self.song_pack_filter_var, values=[]
        )
        self.song_pack_filter_var.trace_variable("w", self.update_scrollable_song_frame)

        # Song Checklist Frame
        self.songs_checkbox_frame = customtkinter.CTkScrollableFrame(master=self)
        self.songs_checkbox_frame.grid_columnconfigure(0, weight=1)
        self.songs_checkbox_frame.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Bottom Bar Frame
        self.bottom_bar_frame = customtkinter.CTkFrame(master=self, height=9)
        self.bottom_bar_frame.grid_rowconfigure(0, weight=1)
        self.bottom_bar_frame.grid_columnconfigure(0, weight=1)

        # Root Grid Layout (UI elements in descending order)
        self.mod_directory_combobox.grid(
            row=1, column=0, padx=(20, 2.5), pady=(10, 5), sticky="ew"
        )
        self.browse_button.grid(
            row=1, column=1, padx=(2.5, 20), pady=(10, 5), sticky="ew"
        )
        self.song_pack_filter_optionmenu.grid(
            row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew"
        )
        self.search_bar.grid(
            row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew"
        )
        self.songs_checkbox_frame.grid(
            row=4, column=0, columnspan=2, padx=20, pady=5, sticky="nsew"
        )
        self.bottom_bar_frame.grid(
            row=5, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="ew"
        )

    def set_window_size(self) -> str:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width_percent = 40
        height_percent = 70
        width = (screen_width * width_percent) // 100
        height = (screen_height * height_percent) // 100

        return f"{width}x{height}+{screen_width // 2 - width // 2}+{screen_height // 2 - height // 2}"

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

            if directory_path == "":
                quit()

            self.submit_mod_directory()

    # noinspection PyUnusedLocal
    def update_scrollable_song_frame(self, *args):
        self.clear_song_list_frame()

        mod_pv_db_scanner = ModPvDbScanner(self.mod_directory_var.get())
        songs = mod_pv_db_scanner.get_all_songs()

        song_packs = set()
        selected_pack = self.song_pack_filter_var.get()

        populate_option_menu = not self.song_pack_filter_optionmenu_populated

        progress_bar = ProgressBar(self.bottom_bar_frame, len(songs), self.winfo_width())

        search_text = self.search_bar.get().lower()

        for index, song in enumerate(songs):
            if not self.song_pack_filter_optionmenu_populated:
                song_packs.add(song.pack)

            if search_text.lower() not in song.name.lower():
                continue

            if selected_pack == "All" or song.pack == selected_pack:
                checkbox_var = customtkinter.IntVar(value=song.state)
                song_widget = SongWidget(
                    self.songs_checkbox_frame,
                    song,
                    checkbox_var,
                    lambda v=checkbox_var, s=song: self.checkbox_toggled(v, s),
                )
                song_widget.show(index, 0)

                if song.state == 1:
                    song_widget.check()

                song_packs.add(song.pack)
                self.song_widgets.append(song_widget)

                progress_bar.update()
                self.update_idletasks()
            else:
                song_widget = SongWidget(self.songs_checkbox_frame, song, None, None)
                song_widget.hide()

        progress_bar.update()
        if populate_option_menu:
            self.populate_song_pack_option_menu(song_packs)
            self.song_pack_filter_optionmenu_populated = True

        self.update_idletasks()

        #  TODO: Find a way to un-cringe this (using protected field)
        self.songs_checkbox_frame._parent_canvas.yview_moveto(0)

    def populate_song_pack_option_menu(self, song_packs):
        self.song_pack_filter_optionmenu.configure(
            values=["All"] + sorted(list(song_packs))
        )

    def clear_song_list_frame(self):
        for song_widget in self.song_widgets:
            if song_widget:
                song_widget.hide()

        self.song_widgets = []

    def submit_mod_directory(self):
        mod_directory = Path(self.mod_directory_var.get())
        if mod_directory.exists():
            self.update_scrollable_song_frame()

    @staticmethod
    def checkbox_toggled(checkbox_var, song):
        checkbox_state = checkbox_var.get()
        song.state = checkbox_state
        song.update_state()

    def dynamic_search(self, event):
        self.update_scrollable_song_frame()
