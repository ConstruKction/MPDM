import re
import concurrent.futures

from pathlib import Path
from typing import Optional

import toml

from song import Song

PV_ID_RE = re.compile(r'(pv_\d+)')


class ModPvDbScanner:
    def __init__(self, root_folder: str):
        self.root_folder = Path(root_folder)

    def get_all_songs(self) -> list[Song]:
        all_songs = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_mod_pv_db, mod_pv_db_path)
                       for mod_pv_db_path in self.root_folder.rglob("**/mod_pv_db.txt")]

            for future in concurrent.futures.as_completed(futures):
                song_list = future.result()
                all_songs.extend(song_list)

        return all_songs

    def process_mod_pv_db(self, mod_pv_db_path: Path) -> list[Song]:
        if not self.has_script_folder(mod_pv_db_path.parent):
            return []

        return self.create_song_objects(mod_pv_db_path)

    def create_song_objects(self, mod_pv_db_path: Path) -> list[Song]:
        song_list = []
        with mod_pv_db_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if "song_name_en" in line:
                    pv_id = re.search(PV_ID_RE, line).group(1)
                    parts = line.strip().split("=")
                    song_name = parts[1]
                    is_commented_out = line.startswith("#")

                    song = Song(
                        pv_id,
                        song_name,
                        line_number,
                        line_number - 1,  # TODO: This has to be less cringe
                        mod_pv_db_path,
                        0 if is_commented_out else 1,
                        self.get_song_pack_name(
                            Path(f"{mod_pv_db_path.parents[1]}/config.toml")
                        )
                    )
                    song_list.append(song)

        return sorted(song_list, key=lambda s: s.name)

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
