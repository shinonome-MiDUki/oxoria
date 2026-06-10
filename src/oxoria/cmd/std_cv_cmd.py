import sys

from PySide6.QtGui import QPixmap, QImage

import cv2
import numpy as np

from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.cv_api import opencv_convert


class CvProcessAPI:

    @classmethod
    @opencv_convert
    def to_blackwhite(cls,
                      cv_img: np.ndarray=None
                      ) -> np.ndarray:
        greyscale = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2GRAY)
        rtn = cv2.cvtColor(greyscale, cv2.COLOR_GRAY2RGBA)
        return rtn
    
    @classmethod
    @opencv_convert
    def recover_color(cls,
                    cv_img: np.ndarray=None
                    ) -> np.ndarray:
        rtn = cv_img
        return rtn
    
    @classmethod
    @opencv_convert
    def denoise_img(cls,
                    cv_img: np.ndarray=None
                    ) -> np.ndarray:
        rtn = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)
        return rtn
    
    @classmethod
    @opencv_convert
    def custom_operation(cls,
                         cv2_cmd: str,
                         cv_img: np.ndarray=None
                         ) -> np.ndarray:
        ctx = {"cv2": cv2, "np": np, "cv_img": cv_img}
        rtn = eval(cv2_cmd, {}, ctx)
        return rtn
    