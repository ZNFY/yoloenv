import io
import time
from config import session, logger, NIFI_URL, executor

def send_image(output_filename, img_bytes, img_format, retries=3):
    for attempt in range(retries):
        try:
            logger.info(f"尝试发送主视频流到 NiFi: {output_filename}, 尝试 {attempt+1}/{retries}")
            response = session.post(
                NIFI_URL,
                files=[('file', (output_filename, io.BytesIO(img_bytes), f'image/{img_format.lower()}'))],
                timeout=10
            )
            if response.status_code == 200:
                return True
            logger.error(f"发送主视频流失败 {response.status_code}")
        except Exception as e:
            logger.error(f"发送主视频流失败: {str(e)}")
            if attempt == retries - 1:
                raise
        time.sleep(2)
    return False

def send_hardcase(base_name, ext_name, original_bytes, img_bytes, img_format):
    # 原始图
    hardcase_original_filename = f"{base_name}--hardcase-original{ext_name}"
    executor.submit(
        session.post, NIFI_URL,
        files=[('file', (hardcase_original_filename, io.BytesIO(original_bytes), f'image/{img_format.lower()}'))],
        timeout=10
    )
    logger.info(f"低置信度，额外异步发送原始图片: {hardcase_original_filename}")

    # 标注图
    hardcase_annotated_filename = f"{base_name}--hardcase-annotated{ext_name}"
    executor.submit(
        session.post, NIFI_URL,
        files=[('file', (hardcase_annotated_filename, io.BytesIO(img_bytes), f'image/{img_format.lower()}'))],
        timeout=10
    )
    logger.info(f"低置信度，额外异步发送画框图片: {hardcase_annotated_filename}")
