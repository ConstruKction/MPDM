import linecache
from pathlib import Path


class Song:
    def __init__(
        self,
        name: str,
        line_number_en: int,
        line_number_jp: int,
        mod_pv_db_path: Path,
        state: int,
        pack: str,
    ):
        self.name = name
        self.line_number_en = line_number_en
        self.line_number_jp = line_number_jp
        self.mod_pv_db_path = mod_pv_db_path
        self.state = state
        self.pack = pack

    def update_state(self):
        lines = linecache.getlines(str(self.mod_pv_db_path))

        for line_number in [self.line_number_en, self.line_number_jp]:
            index = line_number - 1
            if 0 <= index < len(lines):
                if self.state == 0 and not lines[index].startswith("#"):
                    lines[index] = "#" + lines[index]
                elif self.state == 1 and lines[index].startswith("#"):
                    lines[index] = lines[index][1:]

        with open(self.mod_pv_db_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        linecache.clearcache()
