import numpy as np
from ultralytics import YOLO
from config import logger
import os

MODEL = None
CURRENT_MODEL_PATH = 'yolov8s.pt' # 使用一个变量来跟踪当前模型的路径

def load_model(model_path):
    """从指定路径加载或重载模型。"""
    global MODEL, CURRENT_MODEL_PATH
    try:
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at: {model_path}")
            return False
            
        MODEL = YOLO(model_path)
        MODEL.conf = 0.1
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        MODEL.predict(dummy_image, verbose=False)
        CURRENT_MODEL_PATH = model_path
        logger.info(f"YOLOv8 model loaded and pre-heated from: {CURRENT_MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {str(e)}")
        return False

def get_model():
    """获取当前加载的模型实例。"""
    global MODEL
    if MODEL is None:
        load_model(CURRENT_MODEL_PATH)
    return MODEL