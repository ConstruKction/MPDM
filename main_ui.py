from customtkinter import (
    CTk,
    IntVar,
    StringVar,
    CTkEntry,
    CTkScrollableFrame,
    CTkFrame,
    CTkButton,
    CTkComboBox,
    CTkOptionMenu,
)

from mod_pv_db_scanner import ModPvDbScanner
from song import Song
from song_filter import SongFilter
from ui_components.progress_bar import ProgressBar
from ui_components.song_widget import SongWidget
from ui_components.file_browser import FileBrowser


class MainUI(CTk):
    def __init__(self):
        super().__init__()
        self.title("MPDM")
        self.geometry(self.set_window_size())
        self.grid_columnconfigure(0, weight=1)
        self.directory_paths_list = []
        self.song_widgets = []
        self.hidden_widgets = False
        self.file_browser = FileBrowser(self)

        # Path ComboBox
        self.mod_directory_var = StringVar()
        self.mod_directory_combobox = CTkComboBox(
            self,
            variable=self.mod_directory_var,
            values=[],
            command=lambda event=None: self.combobox_path_selected(),
        )

        # Song Search Bar
        self.search_bar = CTkEntry(self, placeholder_text="Search")
        self.search_bar.bind("<KeyRelease>", self.filter_song_widgets_by_search_term)

        # Browse Button
        self.browse_button = CTkButton(
            self, text="Browse", command=self.file_browser.browse_file
        )

        # Song Pack Filter OptionMenu
        self.song_pack_filter_var = StringVar()
        self.song_pack_filter_var.set("All")
        self.song_pack_filter_optionmenu = CTkOptionMenu(
            self, variable=self.song_pack_filter_var, values=[]
        )
        self.song_pack_filter_var.trace_variable(
            "w", self.filter_song_widgets_by_song_pack
        )

        # Song Checklist Frame
        self.songs_checkbox_frame = CTkScrollableFrame(master=self)
        self.songs_checkbox_frame.grid_columnconfigure(0, weight=1)
        self.songs_checkbox_frame.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Bottom Bar Frame
        self.bottom_bar_frame = CTkFrame(master=self, height=9)
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
            self.file_browser.submit_mod_directory()

    def create_song_widgets(self, *_args):
        mod_pv_db_scanner = ModPvDbScanner(self.mod_directory_var.get())
        songs = mod_pv_db_scanner.get_all_songs()

        song_packs = set()

        progress_bar = ProgressBar(
            self.bottom_bar_frame, len(songs), self.winfo_width()
        )

        for index, song in enumerate(songs):
            checkbox_var = IntVar(value=song.state)
            song_widget = SongWidget(
                self.songs_checkbox_frame,
                song,
                checkbox_var,
                lambda v=checkbox_var, s=song: self.checkbox_toggled(v, s),
            )
            song_widget.show(index, 0)

            song_packs.add(song.pack)
            self.song_widgets.append(song_widget)

            progress_bar.update()
            self.update_idletasks()

        self.populate_song_pack_option_menu(song_packs)

        #  TODO: Find a way to un-cringe this (using protected field)
        self.songs_checkbox_frame._parent_canvas.yview_moveto(0)

    def filter_song_widgets_by_song_pack(self, *_args):
        selected_pack = self.song_pack_filter_var.get()

        if self.hidden_widgets:
            for index, song_widget in enumerate(self.song_widgets):
                song_widget.show(index, 0)

            self.hidden_widgets = False

        if selected_pack != "All":
            song_filter = SongFilter()
            filtered_song_widgets = song_filter.filter_out_song_pack(
                self.song_widgets, selected_pack
            )

            for song_widget in filtered_song_widgets:
                song_widget.hide()

            self.hidden_widgets = True

        #  TODO: Find a way to un-cringe this (using protected field)
        self.songs_checkbox_frame._parent_canvas.yview_moveto(0)

    def filter_song_widgets_by_search_term(self, *_args):
        search_term = self.search_bar.get().lower()
        selected_pack = self.song_pack_filter_var.get()

        for index, song_widget in enumerate(self.song_widgets):
            if (
                selected_pack == "All"
                and search_term in song_widget.checkbox.cget("text").lower()
            ):
                song_widget.show(index, 0)
            elif search_term in song_widget.checkbox.cget(
                "text"
            ).lower() and selected_pack == song_widget.song_pack_label.cget("text"):
                song_widget.show(index, 0)
            else:
                song_widget.hide()

        #  TODO: Find a way to un-cringe this (using protected field)
        self.songs_checkbox_frame._parent_canvas.yview_moveto(0)

    def populate_song_pack_option_menu(self, song_packs: set[str]):
        self.song_pack_filter_optionmenu.configure(
            values=["All"] + sorted(list(song_packs))
        )

    def destroy_song_widgets(self):
        for song_widget in self.song_widgets:
            if song_widget:
                song_widget.remove()

        self.song_widgets = []

    @staticmethod
    def checkbox_toggled(checkbox_var: IntVar, song: Song):
        checkbox_state = checkbox_var.get()
        song.state = checkbox_state
        song.update_state()

    def dynamic_search(self, _event):
        self.filter_song_widgets_by_search_term()
