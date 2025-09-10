import os
import time
import asyncio
import threading
from flask import Flask, request, jsonify, make_response
from config import channel_last_updated, DETECTION_INTERVAL, logger
from model import get_model
from utils import ensure_extension
from processing import process_single_image
from nifi_client import send_image, send_hardcase
from cleanup import clear_expired_channels

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_images():
    try:
        if request.method != 'POST':
            return make_response("只接受POST请求", 405)
        if 'image' not in request.files:
            return make_response("没有找到图片文件", 400)

        files = request.files.getlist('image')
        original_filenames = [f.filename for f in files]
        original_images_bytes = [f.read() for f in files]
        channel_id = original_filenames[0].split('_')[0]

        ext = os.path.splitext(original_filenames[0])[1].lower()
        img_format = 'JPEG' if ext in ['.jpg', '.jpeg'] else 'PNG' if ext == '.png' else 'JPEG'

        current_time = time.time()
        process_flag = False
        if channel_id not in channel_last_updated or (current_time - channel_last_updated[channel_id]) >= DETECTION_INTERVAL:
            process_flag = True
            channel_last_updated[channel_id] = current_time

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_single_image(original_images_bytes[0], get_model(), img_format, process_flag, channel_id))
        img_bytes, img_format, processing_time, low_conf_flag = result

        output_filename = ensure_extension(original_filenames[0], img_format)

        if not send_image(output_filename, img_bytes, img_format):
            return make_response("发送到NiFi失败", 500)

        if low_conf_flag:
            base_name, ext_name = os.path.splitext(output_filename)
            send_hardcase(base_name, ext_name, original_images_bytes[0], img_bytes, img_format)

        if process_flag:
            logger.info(f"Channel {channel_id} 处理完成: processing_time={processing_time:.2f}s")
            return jsonify({ "message": "处理成功", "channel_id": channel_id, "processing_time": processing_time })
        else:
            logger.info(f"Channel {channel_id} 发送缓存框图片")
            return jsonify({ "message": "发送缓存框图片", "channel_id": channel_id })

    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return make_response(f"发生错误: {str(e)}", 500)

if __name__ == '__main__':
    get_model()
    cleanup_thread = threading.Thread(target=clear_expired_channels, daemon=True)
    cleanup_thread.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
