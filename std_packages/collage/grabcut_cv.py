import cv2
import numpy as np

from PySide6.QtGui import (
    QPixmap, QImage
    )
from PySide6.QtCore import QPoint

def grabcut_operation(img: np.ndarray,
                      crop_start: QPoint,
                      crop_end: QPoint
                      ) -> np.ndarray:
    if img.shape[2] == 4:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    else:
        img_rgb = img
    
    # Ensure image is uint8 type (required by grabCut CV_8UC3 format)
    if img_rgb.dtype != np.uint8:
        img_rgb = img_rgb.astype(np.uint8)

    mask = np.zeros(img_rgb.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    x1, y1 = crop_start.x(), crop_start.y()
    x2, y2 = crop_end.x(), crop_end.y()
    
    x = max(0, min(x1, x2))
    y = max(0, min(y1, y2))
    w = max(1, abs(x2 - x1))
    h = max(1, abs(y2 - y1))
    
    rect = (x, y, w, h)

    cv2.grabCut(img_rgb, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    result = img.copy()
    result[:, :, 3] = result[:, :, 3] * mask2

    return result


def pixmap_conversion(pixmap: QPixmap,
                      crop_start: QPoint,
                      crop_end: QPoint
                      ) -> QPixmap:
    q_image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    img_rgba = np.frombuffer(
        bytes(q_image.bits()), dtype=np.uint8
        ).reshape(
            (q_image.height(), q_image.width(), 4)
        ).copy()
        
    processed_img: np.ndarray = grabcut_operation(
        img=img_rgba,
        crop_start=crop_start,
        crop_end=crop_end
    )
    h, w, ch = processed_img.shape
    q_image_rtn = QImage(processed_img.data, w, h, ch * w, QImage.Format.Format_RGBA8888)
    processed_pixmap = QPixmap.fromImage(q_image_rtn)
    
    return processed_pixmap