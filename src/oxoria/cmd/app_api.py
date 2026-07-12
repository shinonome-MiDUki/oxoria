import sys
import json
import psutil
import subprocess
from pathlib import Path

from oxoria.global_var import GBVar
from oxoria.ui.ux_widgets.settings_dialog import SettingsDialog

class AppAPI:
    def __init__(self):
        pass

    def run_capture_monitor(self) -> None:
        for proc in psutil.process_iter(["cmdline"]):
            cmdl = proc.info["cmdline"]
            if cmdl and cmdl[0] == "Oxoria Screen Capture Monitor":
                print("working")
                return None
        tasktray_script = Path(__file__).resolve().parents[1] / "ui/tasktray/tasktray_ui.py"
        subprocess.Popen([sys.executable, str(tasktray_script)], start_new_session=True)

    def open_new_window(self) -> None:
        app_root_dir = Path(__file__).resolve().parents[1]
        entry_script = app_root_dir / "__main__.py"
        if not entry_script.exists():
            print("Entry script not found")
            return  
        subprocess.Popen([sys.executable, str(entry_script)], start_new_session=True)

    def open_settings(self) -> None:
        settings_dialog = SettingsDialog()
        settings_dialog.draw_dialog()
        settings_dialog.exec()

    def quit_app(self) -> None:
        main_app = GBVar.MAIN_APP
        if main_app is not None:
            main_app.quit()

    def get_command_stack(self,
                          output_length: int = -1
                          ) -> list[str]:
        command_stack = GBVar.COMMAND_STACK
        if not command_stack:
             return []
        output_length = len(command_stack) if output_length == -1 or output_length > len(command_stack) else output_length
        return command_stack[-1 * output_length]
    

    def mycommand(self,
                  cmd: str,
                  shortcut_alphabet: str
                  ) -> None:
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        if "mycommand" not in app_config:
            app_config["mycommand"] = {}
        app_config["mycommand"][shortcut_alphabet] = cmd
        with open(app_config_file, "w", encoding="utf-8") as f:
            json.dump(app_config, f, ensure_ascii=False, indent=2)

    def get_mycommand(self,
                      shortcut_alphabet: str
                      ) -> str:
        data_dir = GBVar.DATA_DIR
        app_config_file = Path(data_dir).resolve().parent / "config/app_config.json"
        with open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.load(f)
        if "mycommand" not in app_config:
            return ""
        return app_config["mycommand"].get(shortcut_alphabet, "")

    