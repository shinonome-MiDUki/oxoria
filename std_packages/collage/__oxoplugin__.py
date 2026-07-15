from pathlib import Path
import sys

self_dir = str(Path(__file__).resolve().parent)
if self_dir not in sys.path:
    sys.path.append(self_dir)
from collage_ui import CollagePluginUi

CollagePluginUi().exec()