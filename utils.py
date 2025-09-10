import os
import cv2
import numpy as np
from config import logger, TARGET_RESOLUTION

def ensure_extension(filename, format):
    name = os.path.splitext(filename)[0]
    return f"{name}.{format.lower()}"

def resize_to_480p(image, target_width=854, target_height=480):
    try:
        h, w = image.shape[:2]
        scale = target_height / h
        new_w, new_h = int(w * scale), int(h * scale)
        if new_w > target_width:
            scale = target_width / w
            new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        x_offset = (target_width - new_w) // 2
        y_offset = (target_height - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return canvas
    except Exception as e:
        logger.error(f"调整分辨率失败: {str(e)}")
        raise

def draw_boxes(image_np, boxes):
    for box in boxes:
        x1, y1, x2, y2 = map(int, box['xyxy'])
        conf = box['conf']
        label = f"person {conf:.2f}"
        cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 0, 255), 2)
        (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top_left = (x1, y1 - label_height - baseline)
        bottom_right = (x1 + label_width, y1)
        if top_left[1] < 0:
            top_left = (x1, y1)
            bottom_right = (x1 + label_width, y1 + label_height + baseline)
        cv2.rectangle(image_np, top_left, bottom_right, (0, 0, 255), -1)
        text_pos = (x1, y1 - baseline if y1 - baseline > 0 else y1 + label_height)
        cv2.putText(image_np, label, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
