from pathlib import Path
from tkinter import filedialog

import customtkinter

from mod_pv_db_scanner import ModPvDbScanner


class MainUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("MPDM")
        self.geometry(self.set_window_size())
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.directory_paths_list = []  # For ComboBox dropdown memory
        self.song_widgets = []
        self.song_pack_filter_optionmenu_populated = False

        # Path ComboBox
        self.mod_directory_var = customtkinter.StringVar()
        self.mod_directory_label = customtkinter.CTkLabel(
            self, text="Mod Directory Path", fg_color="transparent"
        )
        self.mod_directory_combobox = customtkinter.CTkComboBox(
            self,
            variable=self.mod_directory_var,
            values=[],
            command=lambda event=None: self.combobox_path_selected(),
        )

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

        # Root Grid Layout
        self.mod_directory_label.grid(
            row=0, column=0, padx=20, pady=(5, 0), sticky="ew"
        )
        self.mod_directory_combobox.grid(row=1, column=0, padx=(20, 2.5), sticky="ew")
        self.browse_button.grid(row=1, column=1, padx=(2.5, 20), pady=5, sticky="ew")
        self.song_pack_filter_optionmenu.grid(
            row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew"
        )
        self.songs_checkbox_frame.grid(
            row=3, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="nsew"
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

        for index, song in enumerate(songs):
            if not self.song_pack_filter_optionmenu_populated:
                song_packs.add(song.pack)

            if selected_pack == "All" or song.pack == selected_pack:
                checkbox_var = customtkinter.IntVar(value=song.state)
                checkbox = customtkinter.CTkCheckBox(
                    master=self.songs_checkbox_frame,
                    text=song.name,
                    variable=checkbox_var,
                    command=lambda v=checkbox_var, s=song: self.checkbox_toggled(v, s),
                )

                if song.state == 1:
                    checkbox.select()

                checkbox.grid(row=index, column=0, padx=(0, 5), pady=(0, 5), sticky="w")

                song_pack_label = customtkinter.CTkLabel(
                    master=self.songs_checkbox_frame, text=song.pack
                )
                song_pack_label.grid(
                    row=index, column=1, padx=(5, 0), pady=(0, 5), sticky="w"
                )

                song_packs.add(song.pack)
                self.song_widgets.append((checkbox, song_pack_label))
            else:
                checkbox, song_pack_label = None, None
                self.song_widgets.append((checkbox, song_pack_label))

        if populate_option_menu:
            self.populate_song_pack_option_menu(song_packs)
            self.song_pack_filter_optionmenu_populated = True

        #  TODO: Find a way to un-cringe this (using protected field)
        self.songs_checkbox_frame._parent_canvas.yview_moveto(0)

    def populate_song_pack_option_menu(self, song_packs):
        self.song_pack_filter_optionmenu.configure(
            values=["All"] + sorted(list(song_packs))
        )

    def clear_song_list_frame(self):
        for checkbox, song_pack_label in self.song_widgets:
            if checkbox and song_pack_label:
                checkbox.grid_forget()
                song_pack_label.grid_forget()

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
