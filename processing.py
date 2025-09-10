import cv2
import numpy as np
import asyncio
import time
from config import executor, logger, channel_last_boxes
from utils import resize_to_480p, draw_boxes

async def process_single_image(image_bytes, model, img_format, process_flag, channel_id):
    try:
        start_time = time.time()
        image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image_np is None:
            raise ValueError("无法解码图片")
        image_np = resize_to_480p(image_np)

        boxes, low_conf_flag = [], False

        if process_flag:
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            results = await asyncio.get_event_loop().run_in_executor(
                executor, lambda: model.predict(image_rgb)
            )
            for r in results:
                for box in r.boxes:
                    if model.names[int(box.cls[0])] == 'person':
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = box.conf[0].item()
                        boxes.append({'xyxy': [x1, y1, x2, y2], 'conf': conf})
                        if conf < 0.4:
                            low_conf_flag = True
            channel_last_boxes[channel_id] = boxes
            draw_boxes(image_np, boxes)
        else:
            if channel_id in channel_last_boxes:
                draw_boxes(image_np, channel_last_boxes[channel_id])

        if img_format == 'JPEG':
            success, encoded_image = cv2.imencode('.jpg', image_np)
        elif img_format == 'PNG':
            success, encoded_image = cv2.imencode('.png', image_np)
        else:
            success, encoded_image = cv2.imencode('.jpg', image_np)
            img_format = 'JPEG'
        if not success:
            raise ValueError("无法编码图片")

        img_bytes = encoded_image.tobytes()
        processing_time = time.time() - start_time if process_flag else 0

        return img_bytes, img_format, processing_time, low_conf_flag
    except Exception as e:
        logger.error(f"处理图片时发生错误: {str(e)}")
        raise
