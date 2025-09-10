import numpy as np
from ultralytics import YOLO
from config import logger

MODEL = None

def get_model():
    global MODEL
    if MODEL is None:
        try:
            MODEL = YOLO('yolov8s.pt')
            MODEL.conf = 0.1
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            MODEL.predict(dummy_image, verbose=False)
            logger.info("YOLOv8 模型加载并预热完成")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise
    return MODEL
