import os
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = str(Path(__file__).parent)
logger.debug(f"ROOT_DIR 类型: {type(ROOT_DIR)}")
logger.debug(f"ROOT_DIR 值: {ROOT_DIR}")

# 存储目录配置
STORAGE_DIR = str(os.getenv('GENCOURSEWARE_STORAGE_DIR', os.path.join(ROOT_DIR, 'storage')))
logger.debug(f"STORAGE_DIR 类型: {type(STORAGE_DIR)}")
logger.debug(f"STORAGE_DIR 值: {STORAGE_DIR}")

CACHE_DIR = str(os.path.join(STORAGE_DIR, 'cache'))
logger.debug(f"CACHE_DIR 类型: {type(CACHE_DIR)}")
logger.debug(f"CACHE_DIR 值: {CACHE_DIR}")

OUTPUT_DIR = str(os.path.join(STORAGE_DIR, 'output'))
logger.debug(f"OUTPUT_DIR 类型: {type(OUTPUT_DIR)}")
logger.debug(f"OUTPUT_DIR 值: {OUTPUT_DIR}")

TEMP_DIR = str(os.path.join(STORAGE_DIR, 'temp'))
logger.debug(f"TEMP_DIR 类型: {type(TEMP_DIR)}")
logger.debug(f"TEMP_DIR 值: {TEMP_DIR}")

# 确保存储目录存在
for dir_path in [STORAGE_DIR, CACHE_DIR, OUTPUT_DIR, TEMP_DIR]:
    logger.debug(f"创建目录: {dir_path}")
    os.makedirs(dir_path, exist_ok=True)

# 视频生成配置
VIDEO_CONFIG = {
    'width': 1920,
    'height': 1080,
    'fps': 30,
    'background_color': (255, 255, 255),
    'text_color': (0, 0, 0),
    'title_font_size': 60,
    'content_font_size': 40
}

# API 配置
API_CONFIG = {
    'url': "https://api.deepseek.com/v1/chat/completions",
    'model': "deepseek-chat",
    'temperature': 0.7
}

# 内容生成配置
CONTENT_CONFIG = {
    'max_chunk_length': 2000,
    'min_slides': 3,
    'max_slides': 20
} 