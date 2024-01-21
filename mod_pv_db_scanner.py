from pathlib import Path
from typing import Optional

import toml


class ModPvDbScanner:
    def __init__(self, root_folder: str):
        self.root_folder = Path(root_folder)

    def get_all_songs(self) -> list[tuple[str, str, int, int]]:
        all_songs = []

        for mod_pv_db_path in self.root_folder.rglob("**/mod_pv_db.txt"):
            if not self.has_script_folder(mod_pv_db_path.parent):
                continue

            songs_in_pack = self.read_song_names(mod_pv_db_path)
            song_pack = self.get_song_pack_name(
                Path(f"{mod_pv_db_path.parents[1]}/config.toml")
            )

            for song, is_enabled, line_number in songs_in_pack:
                song_tuple = (song, song_pack, is_enabled, line_number)
                all_songs.append(song_tuple)

        return all_songs

    @staticmethod
    def read_song_names(mod_pv_db_path: Path) -> list[tuple[str, int, int]]:
        song_names = set()
        with mod_pv_db_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if "song_name_en" in line:
                    parts = line.strip().split("=")
                    song_name = parts[1]
                    is_commented_out = line.startswith("#")
                    song_names.add((song_name, 0 if is_commented_out else 1, line_number))

        return sorted(list(song_names), key=lambda x: x[0])

    @staticmethod
    def has_script_folder(directory: Path) -> bool:
        script_directory_path = directory / "script"
        return script_directory_path.exists()

    @staticmethod
    def get_song_pack_name(config_path: Path) -> Optional[str]:
        try:
            with config_path.open("r", encoding="utf-8") as f:
                config_data = toml.load(f)
                return (
                    config_data.get("name")
                    if config_data.get("name")
                    else config_path.parent.name
                )
        except (FileNotFoundError, toml.TomlDecodeError):
            return None
