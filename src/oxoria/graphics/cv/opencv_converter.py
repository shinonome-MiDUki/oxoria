import sys

from PySide6.QtGui import QPixmap, QImage

import cv2
import numpy as np

def opencv_convert(func):
    def wrapper(*args, **kwargs):
        pixmap: QPixmap = kwargs["pixmap"]
        q_image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        img_rgba = np.frombuffer(
            bytes(q_image.bits()), dtype=np.uint8
            ).reshape(
                (q_image.height(), q_image.width(), 4)
            )
        img_bgr = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGR)
        kwargs["cv_img"] = img_bgr
        processed_img: np.ndarray = func(*args, **kwargs)
        h, w, ch = processed_img.shape
        q_image_rtn = QImage(processed_img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_image_rtn)
    return wrapper