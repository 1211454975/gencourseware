import os
import logging
from typing import Optional

def setup_logging(log_level: str = "INFO") -> None:
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def ensure_directory(directory: str) -> None:
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_valid_file(filename: str, allowed_extensions: Optional[list] = None) -> bool:
    """检查文件是否有效（存在且扩展名正确）"""
    if not os.path.exists(filename):
        return False
    
    if allowed_extensions is None:
        return True
        
    return get_file_extension(filename) in allowed_extensions 