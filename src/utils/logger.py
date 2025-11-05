"""日志管理模块"""
import sys
from pathlib import Path
from loguru import logger as _logger
from .config import config


class Logger:
    """日志管理类"""

    def __init__(self):
        self._logger = _logger
        self._setup_logger()

    def _setup_logger(self):
        """配置日志"""
        # 移除默认的handler
        self._logger.remove()

        # 获取日志配置
        log_config = config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_format = log_config.get(
            'format',
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # 添加控制台输出
        self._logger.add(
            sys.stderr,
            format=log_format,
            level=log_level,
            colorize=True
        )

        # 添加文件输出
        log_path = config.get_log_path()
        self._logger.add(
            log_path / "app_{time:YYYY-MM-DD}.log",
            format=log_format,
            level=log_level,
            rotation=log_config.get('rotation', '500 MB'),
            retention=log_config.get('retention', '30 days'),
            compression=log_config.get('compression', 'zip'),
            encoding='utf-8'
        )

        # 添加错误日志文件
        self._logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="ERROR",
            rotation=log_config.get('rotation', '500 MB'),
            retention=log_config.get('retention', '30 days'),
            compression=log_config.get('compression', 'zip'),
            encoding='utf-8'
        )

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """信息日志"""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """错误日志"""
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """异常日志"""
        self._logger.exception(message, **kwargs)

    def get_logger(self):
        """获取原始logger对象"""
        return self._logger


# 全局日志实例
logger = Logger()
