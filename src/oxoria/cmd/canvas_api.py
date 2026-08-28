import os
import json
import shutil
from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPointF

from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.ui.canvas_area.graphics_item import ImageItem

class CanvasAPI:
    def __init__(self):
        pass

    def make_oxoria_file(self) -> dict:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        save_dict = {}
        scene = main_canvas.scene()
        item_list = scene.items()
        for graphics_item in item_list:
            if not isinstance(graphics_item, ImageItem):
                continue
            pointer = graphics_item.pointer
            size_h = graphics_item.img_h
            size_w = graphics_item.img_w
            pos_x = graphics_item.pos().x()
            pos_y = graphics_item.pos().y()
            save_dict[pointer] = {
                "size_h" : size_h,
                "size_w" : size_w,
                "pos_x" : pos_x,
                "pos_y" : pos_y
            }
        return save_dict

        
    def open_resource_on_canvas(self,
                                img_path: str | Path
                                ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        main_canvas.handle_file_drop(path=str(img_path),
                                     event=None,
                                     open_from_ext=True)
        
    def clear_canvas(self) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        for graphics_item in main_canvas.scene().items():
            main_canvas.scene().removeItem(graphics_item)
        GBVar.OPENED_FILE = None

    def wrap_canvas(self,
                    archive_path: str | Path
                    ) -> None:
        if not isinstance(archive_path, Path):
            archive_path = Path(archive_path)
        data_dir = Path(GBVar.DATA_DIR)
        temp_export_dir = data_dir / "temp_export"
        resources_dir = data_dir / "resources_lib"
        temp_export_dir.mkdir(parents=True, exist_ok=True)
        canvas_file_dict = self.make_oxoria_file()
        with open(temp_export_dir / "temp_canvas.oriana", "w", encoding="utf-8") as f:
            json.dump(canvas_file_dict, f)
        current_resources_profile_path = resources_dir / "resources_profile.json"
        if current_resources_profile_path.exists():
            with open(current_resources_profile_path, "r", encoding="utf-8") as f:
                current_resources_profile = json.load(f)
            temp_image_dir = temp_export_dir / "images"
            temp_image_dir.mkdir(parents=True, exist_ok=True)
            archiving_resources_profile = current_resources_profile.copy()
            for pointer in current_resources_profile:
                if pointer not in canvas_file_dict:
                    del archiving_resources_profile[pointer]
                else:
                    img_path = resources_dir / current_resources_profile[pointer]["path"]
                    shutil.copy2(img_path, temp_image_dir)
        else:
            archiving_resources_profile = {}
        with open(temp_export_dir / "temp_resources_profile.json", "w", encoding="utf-8") as f:
            json.dump(archiving_resources_profile, f, ensure_ascii=False)
        shutil.make_archive(archive_path.with_suffix(""), format="zip", root_dir=temp_export_dir)
        os.rename(archive_path.with_suffix(".zip"), archive_path.with_suffix(".oxoarchive"))
        shutil.rmtree(temp_export_dir)

    def delete_item(self,
                    items_to_delete: list[ImageItem]
                    ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        for item in items_to_delete:
            main_canvas.scene().removeItem(item)
        
    def get_selected(self) -> list[ImageItem]:
        main_canvas = UI_Var.MAIN_CANVAS
        selected_items = main_canvas.scene().selectedItems()
        return selected_items
    
    def group_selected(self) -> None:
        main_canvas_scene = UI_Var.MAIN_CANVAS.scene()
        main_canvas_scene.createItemGroup(main_canvas_scene.selectedItems())

    def is_anything_selected(self) -> bool:
        return True if self.get_selected() else False
    
    def set_to_origin(self) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        main_canvas.resetTransform()
        main_canvas.centerOn(0, 0)
        main_canvas.scale(0.15, 0.15) 
    
    def set_pixmap(self,
                   pixmap: QPixmap,
                   image_item: ImageItem
                   ) -> None:
        image_item.base_pixmap = pixmap
        scaled_img = ImageItem.scale_pixmap(pixmap)
        image_item.setPixmap(scaled_img)