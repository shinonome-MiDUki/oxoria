import dataclasses
import json 
from pathlib import Path
from typing import Any, Type

from PySide6 import QtWidgets

from oxoria.global_var import GBVar

@dataclasses.dataclass
class AppConfigAPI:
    semantic_search_length : int = 2
    semantic_search_cutoff : float = 0.65
    distance_search_length : int = 1
    distance_search_cutoff : float = 0.5

    @classmethod
    def init_app_config(cls):
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        return cls(**app_config)
    
    @classmethod
    def set_app_config(cls,
                       attr: str,
                       new_value: Any
                       ) -> None:
        setattr(cls, attr, new_value)
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        app_config[attr] = new_value
        with open(app_config_file, "w", encoding="utf-8") as f:
            json.dump(app_config, f, ensure_ascii=False, indent=2)
    
@dataclasses.dataclass
class EditorConfigAPI:
    handle_size : int = 40   
    handle_color : str = "#4A90D9"
    handle_outline_thickness : float = 1.5
    handle_outline_color : str = "#FFFFFF"  
    min_item_size : int = 40     
    canvas_height : int = 800     
    sidebar_default : int = 200     
    sidebar_min : int = 200     
    sidebar_standby : int = 300
    sidebar_max : int = 700 
    is_draw_ruled_lines : bool = True
    ruled_line_interval : int = 100
    ruled_line_thin_thickness : float = 1.0
    ruled_line_thick_thickness : float = 1.5
    ruled_line_thich_color : str = "#505050"
    ruled_line_thin_color : str = "#3C3C3C"
    scaling_step : float = 0.1
    canvas_bg_color : str = "#1E1E1E"
    image_item_frame_color : str = "#4A90D9"
    image_item_frame_thickness : float = 4.0
    memo_paper_color : str = "#FFFDF0"
    memo_text_color : str = "#333333"
    memo_text_font_size : int = 180
    memo_text_font : str = "Yu Gothic"
    memo_text_margin : int = 20
    command_line_text_color : str = "#FFFFFF"
    command_line_bg_color : str = "#303030"
    splitter_handle_width : int = 10

    @classmethod
    def init_editor_config(cls) :
        data_dir = GBVar.DATA_DIR
        editor_config_file = Path(data_dir).resolve().parent / "config/editor_config.json"
        with open(editor_config_file, "r", encoding="utf-8") as f:
            editor_config = json.load(f)
        editor_config = editor_config.get("editor")
        return cls(**editor_config)
    
    @classmethod
    def set_app_config(cls,
                       attr: str,
                       new_value: Any
                       ) -> None:
        setattr(cls, attr, new_value)
        data_dir = GBVar.DATA_DIR
        editor_config_file = Path(data_dir).resolve().parent / "config/editor_config.json"
        with open(editor_config_file, "r", encoding="utf-8") as f:
            editor_config = json.load(f)
        editor_config["editor"][attr] = new_value
        with open(editor_config_file, "w", encoding="utf-8") as f:
            json.dump(editor_config, f, ensure_ascii=False, indent=2)
