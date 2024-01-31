from typing import Any, Callable, Optional

from customtkinter import IntVar, CTkCheckBox, CTkLabel

from song import Song


class SongWidget:
    def __init__(
        self,
        master: Any,
        song: Song,
        checkbox_var: Optional[IntVar],
        checkbox_command: Optional[Callable],
    ):
        self.checkbox_var = checkbox_var
        self.checkbox = CTkCheckBox(
            master=master,
            text=song.name,
            variable=self.checkbox_var,
            command=checkbox_command,
        )

        self.song_pack_label = CTkLabel(master=master, text=song.pack)
        self.checkbox.select() if song.state else 0

    def show(self, row: int, column: int):
        self.checkbox.grid(row=row, column=column, padx=(0, 5), pady=(0, 5), sticky="w")
        self.song_pack_label.grid(
            row=row, column=column + 1, padx=(5, 0), pady=(0, 5), sticky="w"
        )

    def hide(self):
        self.checkbox.grid_forget()
        self.song_pack_label.grid_forget()

    def remove(self):
        self.checkbox.destroy()
        self.song_pack_label.destroy()
