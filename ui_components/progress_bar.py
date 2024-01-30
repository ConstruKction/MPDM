from math import floor
from typing import Any

from customtkinter import CTkProgressBar


class ProgressBar:
    def __init__(self, master: Any, total_songs: int, window_width: int):
        self.total_songs = total_songs
        self.progress_step = 1 / total_songs
        self.current_progress = 0
        self.progress_bar = CTkProgressBar(master=master, width=self.set_width(window_width))
        self.create()

    def create(self):
        self.progress_bar.grid(
            row=5, column=0, columnspan=3, sticky="ew"
        )

    def update(self):
        self.current_progress += self.progress_step
        self.progress_bar.set(floor(self.current_progress * 1000) / 1000)

    @staticmethod
    def set_width(window_width: int) -> int:
        return (window_width * 100) // 100
