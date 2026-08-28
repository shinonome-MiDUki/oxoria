from pathlib import Path

from PySide6.QtCore import (
    QFile, QDataStream, QIODevice, 
    QBuffer, QByteArray, QPointF
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.ui.ui_var import UI_Var
from oxoria.ui.canvas_area.graphics_item import ImageItem

class IoAPI:
    
    @staticmethod
    def save_oxoria_file(saving_path: str) -> None:
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
            data_bytes = byte_array.data()
            stream.writeUInt32(len(data_bytes))    
            stream.writeBytes(data_bytes) 
            
        file.close()

    @staticmethod
    def open_oxoria_file(opening_path: str | Path) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        file = QFile(opening_path)
        if not file.open(QIODevice.ReadOnly):
            raise IOError(f"File reading error : {opening_path}")
            
        stream = QDataStream(file)
        
        magic = stream.readUInt32()
        if magic != 0x4F584F52:
            raise ValueError("Invalid file format (Header error)")
        version = stream.readUInt32()
        print(f"version : {version}")

        CanvasAPI().clear_canvas()
        
        count = stream.readInt32()
        print(f"count : {count}")
        for _ in range(count):
            item_type = stream.readQString()
            
            if item_type == "pixmap":
                x = stream.readDouble()
                y = stream.readDouble()
                scale = stream.readDouble()
                rotation = stream.readDouble()
                z_value = stream.readDouble()

                byte_len = stream.readUInt32()       
                raw_data = stream.readBytes(byte_len)
                image = QImage.fromData(raw_data)
                pixmap = QPixmap.fromImage(image)

                item = ImageItem(
                    pixmap=pixmap,
                    pos=QPointF(x, y)
                )
                item.setScale(scale)
                item.setRotation(rotation)
                item.setZValue(z_value)
                
                main_canvas.scene().addItem(item)

        file.close()