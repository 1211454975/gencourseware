import os
from pathlib import Path

# 获取项目根目录
ROOT_DIR = str(Path(__file__).parent)

# 存储目录配置
STORAGE_DIR = str(os.getenv('GENCOURSEWARE_STORAGE_DIR', os.path.join(ROOT_DIR, 'storage')))
CACHE_DIR = str(os.path.join(STORAGE_DIR, 'cache'))
OUTPUT_DIR = str(os.path.join(STORAGE_DIR, 'output'))
TEMP_DIR = str(os.path.join(STORAGE_DIR, 'temp'))

# 确保存储目录存在
for dir_path in [STORAGE_DIR, CACHE_DIR, OUTPUT_DIR, TEMP_DIR]:
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