from pathlib import Path

from PySide6.QtCore import QFile, QDataStream, QIODevice, QBuffer, QByteArray
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.ui.ui_var import UI_Var

class IoAPI:
    
    @staticmethod
    def save_oxoria_file(self, 
                        saving_path: str
                        ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        file = QFile(saving_path)
        if not file.open(QIODevice.WriteOnly):
            raise IOError(f"File writing error : {saving_path}")
            
        stream = QDataStream(file)
        stream.writeUInt32(0x4F584F52) 
        stream.writeUInt32(1)          
    
        items = [item for item in main_canvas.scene().items() if isinstance(item, QGraphicsPixmapItem)]
        stream.writeInt32(len(items))
        
        for item in items:
            stream.writeQString("pixmap")
            
            stream.writeDouble(item.x())
            stream.writeDouble(item.y())
            stream.writeDouble(item.scale())
            stream.writeDouble(item.rotation())
            stream.writeDouble(item.zValue())
            
            pixmap = item.pixmap()
            image = pixmap.toImage()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            image.save(buffer, "PNG")

            stream.writeByteArray(byte_array)
            
        file.close()

    @staticmethod
    def open_oxoria_file(self, 
                        opening_path: str | Path
                        ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        file = QFile(opening_path)
        if not file.open(QIODevice.ReadOnly):
            raise IOError(f"File reading error : {opening_path}")
            
        stream = QDataStream(file)
        
        magic = stream.readUInt32()
        if magic != 0x4F584F52:
            raise ValueError("Invalid file format (Header error)")
        version = stream.readUInt32()

        CanvasAPI().clear_canvas()
        
        count = stream.readInt32()
        for _ in range(count):
            item_type = stream.readQString()
            
            if item_type == "pixmap":
                x = stream.readDouble()
                y = stream.readDouble()
                scale = stream.readDouble()
                rotation = stream.readDouble()
                z_value = stream.readDouble()
                byte_array = stream.readByteArray()
                image = QImage.fromData(byte_array)
                pixmap = QPixmap.fromImage(image)
                
                item = QGraphicsPixmapItem(pixmap)
                item.setPos(x, y)
                item.setScale(scale)
                item.setRotation(rotation)
                item.setZValue(z_value)
                
                main_canvas.scene().addItem(item)
                
        file.close()