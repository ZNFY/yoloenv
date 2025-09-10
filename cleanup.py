import time
from config import channel_last_updated, channel_last_boxes, TIMEOUT_SECONDS, logger

def clear_expired_channels():
    while True:
        current_time = time.time()
        expired_channels = [
            channel for channel, last_time in channel_last_updated.items()
            if (current_time - last_time) >= TIMEOUT_SECONDS
        ]
        for channel in expired_channels:
            del channel_last_updated[channel]
            if channel in channel_last_boxes:
                del channel_last_boxes[channel]
            logger.info(f"Channel {channel} timed out")
        time.sleep(10)
