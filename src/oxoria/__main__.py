import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QPixmap, QIcon
import setproctitle

from oxoria.ui.main_ui import MainWindow
from oxoria.ui.initial.initialise_ui import InitUI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI
from oxoria.global_var import GBVar

def check_first_run() -> bool:
    settings = QSettings("App", "oxoria")
    if settings.value("first_run", "true") == "true" or not settings.value("central_repo_dir", ""):
        settings.setValue("first_run", "false")
        return True
    return False

def run_program():
    load_dotenv()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationDisplayName("OXORIA 2026")
    app.setApplicationName("OXORIA_2026")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "_resources/assets/icon.png")))

    splash_img_path = Path(__file__).resolve().parent / "_resources/assets/initial_image.jpg"
    splash = QSplashScreen(QPixmap(str(splash_img_path)))
    splash.show()
    splash.showMessage("Loading transformers", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    
    search_api = SearchAPI()
    setproctitle.setproctitle("Oxoria 2026")
    if check_first_run():
        win = InitUI()
    else:
        if QSettings("App", "oxoria").value("use_capture_monitor", "true") == "true":
            app_api = AppAPI()
            app_api.run_capture_monitor()
        win = MainWindow()
    win.show()
    GBVar.MAIN_APP = app  
    splash.finish(win)  
    sys.exit(app.exec())

def main():
    parser = argparse.ArgumentParser(description="Oxoria 2026")
    parser.add_argument("-r", "--reset", action="store_true", help="reset oxoria")
    parser.add_argument("-d", "--delete", action="store_true", help="delete repository")
    args = parser.parse_args()

    if args.reset:
        settings = QSettings("App", "oxoria")
        if settings.value("first_run", "true") == "true":
            return
        settings.setValue("first_run", "true")
        if args.delete:
            central_repo_dir = settings.value("central_repo_dir", "")
            if not central_repo_dir:
                print("central_repo_dir not set")
                return
            print(f"Are you sure that you want to permanantly delete {central_repo_dir} ?")
            confirmation = str(input("Yes/[No] : "))
            if confirmation not in ["Yes", "YES"]:
                return
            import shutil
            shutil.rmtree(central_repo_dir)
        return
    run_program()


if __name__ == "__main__":
    main()