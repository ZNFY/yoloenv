import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 日志配置
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 常量
NIFI_URL = "http://10.19.2.139:30033"
TIMEOUT_SECONDS = 10
DETECTION_INTERVAL = 1.0
TARGET_RESOLUTION = (854, 480)

# 线程池
executor = ThreadPoolExecutor(max_workers=max(4, multiprocessing.cpu_count()))

# 通道缓存
channel_last_updated = {}
channel_last_boxes = {}

# 带重试的 HTTP 会话
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
