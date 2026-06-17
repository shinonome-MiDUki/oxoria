import dataclasses
import json
from pathlib import Path

from PySide6.QtCore import QSettings

from oxoria.global_var import GBVar

@dataclasses.dataclass
class ConfigAPI:
    resources_lib : str = "resources_lib"

    def switch_resources_lib(self,
                             new_lib_name: str
                             ) -> None:
        self.resources_lib = new_lib_name
        GBVar.RESOURCES_DIR = new_lib_name
        QSettings("App", "oxoria").setValue("resources_lib", new_lib_name)


    def make_resources_lib(self,
                           new_lib_name: str
                           ) -> None:
        new_resources_lib_dir = Path(GBVar.DATA_DIR) / new_lib_name
        if new_resources_lib_dir.exists():
            print("Already Exist")
            return
        new_resources_lib_dir.mkdir(parents=True)
        with open(new_resources_lib_dir / "resources_profile.json", "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        self.switch_resources_lib(new_lib_name=new_lib_name)

    
    