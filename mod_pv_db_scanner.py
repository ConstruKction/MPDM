from pathlib import Path
from typing import Optional

import toml

from song import Song


class ModPvDbScanner:
    def __init__(self, root_folder: str):
        self.root_folder = Path(root_folder)

    def get_all_songs(self) -> list[Song]:
        all_songs = []
        for mod_pv_db_path in self.root_folder.rglob("**/mod_pv_db.txt"):
            if not self.has_script_folder(mod_pv_db_path.parent):
                continue

            all_songs = self.create_song_objects(mod_pv_db_path)

        return all_songs

    def create_song_objects(self, mod_pv_db_path: Path) -> list[Song]:
        song_list = []
        with mod_pv_db_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if "song_name_en" in line:
                    parts = line.strip().split("=")
                    song_name = parts[1]
                    is_commented_out = line.startswith("#")
                    song = Song(
                        song_name,
                        line_number,
                        line_number - 1,
                        mod_pv_db_path,
                        0 if is_commented_out else 1,
                        self.get_song_pack_name(
                            Path(f"{mod_pv_db_path.parents[1]}/config.toml")
                        ),
                    )
                    song_list.append(song)

        return song_list

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
