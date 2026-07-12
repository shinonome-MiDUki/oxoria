import dataclasses
import json 
from pathlib import Path
from typing import Any

from oxoria.global_var import GBVar


@dataclasses.dataclass
class AppConfigAPI:
    semantic_search_length : int = 2
    semantic_search_cutoff : float = 0.65
    distance_search_length : int = 1
    distance_search_cutoff : float = 0.5
    command_stack_length : int = 15

    @classmethod
    def init_config(cls):
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        app_config = app_config.get("app")
        return cls(**app_config)
    
    @classmethod
    def set_config(cls,
                   attr: str,
                   new_value: Any
                   ) -> None:
        setattr(cls, attr, new_value)
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        app_config["app"][attr] = new_value
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
    def init_config(cls) :
        data_dir = GBVar.DATA_DIR
        editor_config_file = Path(data_dir).resolve().parent / "config/editor_config.json"
        with open(editor_config_file, "r", encoding="utf-8") as f:
            editor_config = json.load(f)
        editor_config = editor_config.get("editor")
        return cls(**editor_config)
    
    @classmethod
    def set_config(cls,
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

class UseConfigData:
    _editor_config_instance = None
    _app_config_instance = None

    @classmethod
    def app_config(cls):
        if cls._app_config_instance is None:
            cls._app_config_instance = AppConfigAPI.init_config()
        return cls._app_config_instance

    @classmethod
    def editor_config(cls):
        if cls._editor_config_instance is None:
            cls._editor_config_instance = EditorConfigAPI.init_config()
        return cls._editor_config_instance
    
    @classmethod
    def set_config(cls,
                   sector: str,
                   attr_name: str,
                   new_value: Any
                   ) -> None:
        if sector == "editor":
            ConfigAPI = EditorConfigAPI
        elif sector == "app":
            ConfigAPI = AppConfigAPI
        else:
            return None
        ConfigAPI.set_config(
            attr=attr_name,
            new_value=new_value
        )
        