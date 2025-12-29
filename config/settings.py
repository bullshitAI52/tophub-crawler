"""
爬虫配置设置
"""

# 基础设置
BASE_URL = "https://tophub.today"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# 延迟设置（秒）
MIN_DELAY = 1.0
MAX_DELAY = 3.0

# 用户代理池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]

# 请求头模板
HEADERS_TEMPLATE = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# 数据保存设置
OUTPUT_DIR = "data"
OUTPUT_FORMAT = "json"  # json, csv, both
ENABLE_TIMESTAMP = True

# 爬取限制
MAX_ITEMS_PER_PLATFORM = 50
MAX_PLATFORMS_PER_RUN = 5

# 调试模式
DEBUG = False
SAVE_DEBUG_HTML = False
SAVE_SCREENSHOTS = False

# 代理设置（如果需要）
PROXY_ENABLED = False
PROXY_LIST = []  # 格式: ['http://user:pass@host:port', ...]

# Selenium设置（如果使用）
SELENIUM_SETTINGS = {
    'headless': True,
    'window_size': (1920, 1080),
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'chrome_driver_path': None,  # 自动检测
}