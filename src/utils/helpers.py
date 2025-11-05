"""辅助函数模块"""
import random
import time
from datetime import datetime, time as dt_time
from typing import List, Any, Dict
import pytz
from .config import config


def random_delay(min_seconds: float = None, max_seconds: float = None):
    """
    随机延迟

    Args:
        min_seconds: 最小延迟秒数
        max_seconds: 最大延迟秒数
    """
    if min_seconds is None:
        min_seconds = config.get('crawler.delay.min', 1)
    if max_seconds is None:
        max_seconds = config.get('crawler.delay.max', 3)

    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def get_random_user_agent() -> str:
    """获取随机User-Agent"""
    user_agents = config.get('crawler.user_agents', [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    ])
    return random.choice(user_agents)


def is_trading_day() -> bool:
    """
    判断当前是否为交易日（简化版，仅判断工作日）

    Returns:
        是否为交易日
    """
    tz = pytz.timezone(config.get('scheduler.timezone', 'Asia/Shanghai'))
    now = datetime.now(tz)
    # 0=周一, 6=周日
    return now.weekday() < 5


def is_trading_time() -> bool:
    """
    判断当前是否在交易时间内

    Returns:
        是否在交易时间
    """
    if not is_trading_day():
        return False

    tz = pytz.timezone(config.get('scheduler.timezone', 'Asia/Shanghai'))
    now = datetime.now(tz).time()

    trading_hours = config.trading_hours

    # 上午交易时间
    morning_start = datetime.strptime(
        trading_hours.get('morning_start', '09:30'), '%H:%M'
    ).time()
    morning_end = datetime.strptime(
        trading_hours.get('morning_end', '11:30'), '%H:%M'
    ).time()

    # 下午交易时间
    afternoon_start = datetime.strptime(
        trading_hours.get('afternoon_start', '13:00'), '%H:%M'
    ).time()
    afternoon_end = datetime.strptime(
        trading_hours.get('afternoon_end', '15:00'), '%H:%M'
    ).time()

    return (morning_start <= now <= morning_end) or \
           (afternoon_start <= now <= afternoon_end)


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数

    Args:
        value: 待转换的值
        default: 转换失败时的默认值

    Returns:
        浮点数
    """
    if value is None or value == '' or value == '-':
        return default

    try:
        # 移除可能的百分号和逗号
        if isinstance(value, str):
            value = value.replace('%', '').replace(',', '').strip()
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数

    Args:
        value: 待转换的值
        default: 转换失败时的默认值

    Returns:
        整数
    """
    if value is None or value == '' or value == '-':
        return default

    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return int(float(value))
    except (ValueError, TypeError):
        return default


def clean_text(text: str) -> str:
    """
    清理文本

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    if not text:
        return ''
    return text.strip().replace('\n', '').replace('\r', '').replace('\t', ' ')


def format_market_cap(value: float) -> str:
    """
    格式化市值显示

    Args:
        value: 市值（元）

    Returns:
        格式化的字符串
    """
    if value >= 1e12:
        return f"{value / 1e12:.2f}万亿"
    elif value >= 1e8:
        return f"{value / 1e8:.2f}亿"
    elif value >= 1e4:
        return f"{value / 1e4:.2f}万"
    else:
        return f"{value:.2f}"


def retry_on_exception(max_attempts: int = 3, backoff_factor: float = 2):
    """
    装饰器：异常重试

    Args:
        max_attempts: 最大尝试次数
        backoff_factor: 退避因子
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


def chunks(lst: List[Any], n: int):
    """
    将列表分块

    Args:
        lst: 原始列表
        n: 每块大小

    Yields:
        分块后的列表
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_stock_market(code: str) -> str:
    """
    根据股票代码判断所属市场

    Args:
        code: 股票代码

    Returns:
        市场代码 ('SZ' or 'SH')
    """
    if code.startswith(('0', '2', '3')):
        return 'SZ'  # 深圳
    elif code.startswith('6'):
        return 'SH'  # 上海
    else:
        return 'UNKNOWN'


def build_stock_url(code: str) -> str:
    """
    构建股票详情页URL

    Args:
        code: 股票代码

    Returns:
        完整的URL
    """
    market = get_stock_market(code).lower()
    base_url = config.get('eastmoney.stock_detail_base', 'https://quote.eastmoney.com/')
    return f"{base_url}{market}{code}.html"
