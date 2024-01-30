from typing import List

from ui_components.song_widget import SongWidget


class SongFilter:
    @staticmethod
    def filter_out_song_pack(songs_widgets: List[SongWidget], song_pack_from_optionmenu: str) -> List[SongWidget]:
        filtered_song_widgets = []

        for song_widget in songs_widgets:
            if song_widget.song_pack_label.cget("text") != song_pack_from_optionmenu:
                filtered_song_widgets.append(song_widget)

        return filtered_song_widgets
