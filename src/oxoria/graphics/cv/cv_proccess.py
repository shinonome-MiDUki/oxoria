from PySide6.QtGui import QPixmap
import cv2
import numpy as np

from oxoria.graphics.cv.opencv_converter import opencv_convert

class CvProcess:

    @classmethod
    @opencv_convert
    def to_blackwhite(cls,
                      pixmap: QPixmap,
                      cv_img: np.ndarray=None
                      ) -> np.ndarray:
        greyscale = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        rtn = cv2.cvtColor(greyscale, cv2.COLOR_GRAY2RGB)
        return rtn
    
    @classmethod
    @opencv_convert
    def denoise_img(cls,
                    pixmap: QPixmap,
                    cv_img: np.ndarray=None
                    ) -> np.ndarray:
        rtn = cv2.fastNlMeansDenoisingColored(cv_img, None, 10, 10, 7, 21)
        return rtn