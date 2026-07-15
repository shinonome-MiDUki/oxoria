from PySide6.QtGui import QPixmap, QImage

import numpy as np

from oxoria.cmd.canvas_api import CanvasAPI

def opencv_convert(func):
    def wrapper(*args, **kwargs):
        for item in CanvasAPI().get_selected():
            pixmap = item.base_pixmap
            q_image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
            img_rgba = np.frombuffer(
                bytes(q_image.bits()), dtype=np.uint8
                ).reshape(
                    (q_image.height(), q_image.width(), 4)
                )
            kwargs["cv_img"] = img_rgba
            processed_img: np.ndarray = func(*args, **kwargs)
            h, w, ch = processed_img.shape
            q_image_rtn = QImage(processed_img.data, w, h, ch * w, QImage.Format.Format_RGBA8888)
            processed_pixmap = QPixmap.fromImage(q_image_rtn)
            CanvasAPI().set_pixmap(
                 pixmap=processed_pixmap,
                 image_item=item
            )
    return wrapper