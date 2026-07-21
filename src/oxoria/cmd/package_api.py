import importlib
import sys
import shutil
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from oxoria.global_var import GBVar
from oxoria.ui.ui_var import UI_Var
from oxoria.ui.ux_widgets.console_output import OxoriaConsole

class PackageAPI:
    def __init__(self):
        self.plugin_root = Path(GBVar.DATA_DIR).resolve().parent / "plugins"

    def launch_plugin(self,
                      plugin_name: str
                      ) -> None:
        plugin_folder = self.plugin_root / plugin_name
        if not plugin_folder.exists():
            OxoriaConsole.write_console(f"Plugin load error : plugin folder not found")
            return
        entry_pt = plugin_folder / "__oxoplugin__.py"
        if not plugin_folder.exists():
            OxoriaConsole.write_console(f"Plugin load error : __oxoplugin__.py file not found")
            return
        spec = importlib.util.spec_from_file_location(plugin_name, entry_pt)
        if spec is None:
            OxoriaConsole.write_console(f"Plugin load error : plugin not found")
            return
        plugin = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = plugin
        spec.loader.exec_module(plugin)
        OxoriaConsole.write_console(f"Plugin {plugin_name} executed")

    def install_plugin(self,
                       plugin_folder: str,
                       plugin_name: str,
                       make_copy: bool=True,
                       force: bool=False
                       ) -> None:
        if not Path(plugin_folder).exists():
            OxoriaConsole.write_console(f"Plugin load error : plugin folder not found")
            return
        dst_folder = Path(self.plugin_root) / plugin_name
        if not force and dst_folder.exists():
            OxoriaConsole.write_console(f"Plugin load error : folder {plugin_name} already exist")
            return
        if make_copy:
            shutil.copytree(src=plugin_folder, dst=dst_folder)
        else:
            shutil.move(src=plugin_folder, dst=dst_folder)
        OxoriaConsole.write_console(f"Plugin {plugin_name} installed")

    def install_from_browser(self) -> None:
        plugin_folder = QFileDialog.getExistingDirectory(UI_Var.MAIN_CANVAS, "Plugin Folder")
        if not plugin_folder:
            return
        plugin_name = Path(plugin_folder).name
        self.install_plugin(
            plugin_folder=plugin_folder,
            plugin_name=plugin_name
        )