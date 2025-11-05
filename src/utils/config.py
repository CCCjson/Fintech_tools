"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


class Config:
    """配置管理类"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_file = self.base_dir / "config" / "config.yaml"
        self._config: Dict[str, Any] = {}
        self._load_env()
        self._load_yaml()

    def _load_env(self):
        """加载环境变量"""
        env_file = self.base_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    def _load_yaml(self):
        """加载YAML配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键

        Args:
            key: 配置键，如 'app.name' 或 'database.path'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        """获取环境变量"""
        return os.getenv(key, default)

    @property
    def app(self) -> Dict[str, Any]:
        """获取应用配置"""
        return self._config.get('app', {})

    @property
    def database(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self._config.get('database', {})

    @property
    def crawler(self) -> Dict[str, Any]:
        """获取爬虫配置"""
        return self._config.get('crawler', {})

    @property
    def eastmoney(self) -> Dict[str, Any]:
        """获取东方财富网URL配置"""
        return self._config.get('eastmoney', {})

    @property
    def graham(self) -> Dict[str, Any]:
        """获取格雷厄姆算法配置"""
        return self._config.get('graham', {})

    @property
    def scheduler(self) -> Dict[str, Any]:
        """获取调度器配置"""
        return self._config.get('scheduler', {})

    @property
    def trading_hours(self) -> Dict[str, Any]:
        """获取交易时间配置"""
        return self._config.get('trading_hours', {})

    @property
    def api(self) -> Dict[str, Any]:
        """获取API配置"""
        return self._config.get('api', {})

    @property
    def base_path(self) -> Path:
        """获取项目根目录"""
        return self.base_dir

    def get_data_path(self, subdir: str = '') -> Path:
        """获取数据目录路径"""
        path = self.base_dir / "data" / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_log_path(self) -> Path:
        """获取日志目录路径"""
        path = self.base_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path


# 全局配置实例
config = Config()
