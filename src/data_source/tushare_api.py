"""Tushare数据源客户端"""
import time
import pandas as pd
from typing import Optional, List
from functools import wraps
from src.utils.logger import logger

try:
    import tushare as ts
except ImportError:
    raise ImportError("请先安装tushare: pip install tushare")


def rate_limit(calls_per_minute=200):
    """API调用频率限制装饰器"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


def retry_on_error(max_retries=3, delay=1):
    """错误重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"API调用失败，{delay}秒后重试 ({attempt + 1}/{max_retries}): {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator


class TushareClient:
    """Tushare数据源客户端"""

    def __init__(self, token: str = None):
        """
        初始化Tushare客户端

        Args:
            token: Tushare token，如果不提供则从配置文件读取
        """
        if token is None:
            from src.utils.config import config
            token = config.get('tushare.token')

        if not token:
            raise RuntimeError("Tushare token未配置，请提供token或在config/config.yaml中配置tushare.token")

        ts.set_token(token)
        self.pro = ts.pro_api()
        logger.info("Tushare客户端初始化成功")

    # ==================== 基础数据 ====================

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_stock_list(self, market: str = None) -> pd.DataFrame:
        """
        获取股票列表

        Args:
            market: 市场类型 ('SZ', 'SH', None表示全部)

        Returns:
            DataFrame包含: ts_code, symbol, name, area, industry, market, list_date等
        """
        params = {'list_status': 'L'}  # 只获取上市状态的股票

        if market:
            if market.upper() == 'SZ':
                params['exchange'] = 'SZSE'
            elif market.upper() == 'SH':
                params['exchange'] = 'SSE'

        df = self.pro.stock_basic(**params)
        logger.info(f"获取股票列表成功，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_trade_calendar(self, start_date: str, end_date: str, exchange: str = 'SSE') -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            exchange: 交易所 SSE上交所 SZSE深交所

        Returns:
            DataFrame包含: exchange, cal_date, is_open等
        """
        df = self.pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date)
        return df

    # ==================== 行情数据 ====================

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_daily_quotes(self, ts_code: str = None, trade_date: str = None,
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取日线行情数据

        Args:
            ts_code: 股票代码 (如 '600000.SH')
            trade_date: 交易日期 YYYYMMDD
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD

        Returns:
            DataFrame包含: ts_code, trade_date, open, high, low, close, vol, amount等
        """
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.daily(**params)

        if df is not None and not df.empty:
            logger.info(f"获取日线行情成功，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_daily_basic(self, ts_code: str = None, trade_date: str = None,
                        start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取每日指标数据

        Args:
            ts_code: 股票代码
            trade_date: 交易日期 YYYYMMDD
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD

        Returns:
            DataFrame包含: ts_code, trade_date, turnover_rate, pe, pb, total_mv, circ_mv等
        """
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.daily_basic(**params)

        if df is not None and not df.empty:
            logger.info(f"获取每日指标成功，共{len(df)}条")
        return df

    # ==================== 财务数据 ====================

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_income_statement(self, ts_code: str, period: str = None,
                             start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取利润表数据

        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame包含: total_revenue, revenue_yoy, n_income等
        """
        params = {'ts_code': ts_code}
        if period:
            params['period'] = period
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.income(**params)

        if df is not None and not df.empty:
            logger.info(f"获取利润表数据成功: {ts_code}，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_balance_sheet(self, ts_code: str, period: str = None,
                          start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取资产负债表数据

        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame包含: total_assets, total_liab, total_hldr_eqy_exc_min_int等
        """
        params = {'ts_code': ts_code}
        if period:
            params['period'] = period
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.balancesheet(**params)

        if df is not None and not df.empty:
            logger.info(f"获取资产负债表数据成功: {ts_code}，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_cash_flow(self, ts_code: str, period: str = None,
                      start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取现金流量表数据

        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame包含: n_cashflow_act等
        """
        params = {'ts_code': ts_code}
        if period:
            params['period'] = period
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.cashflow(**params)

        if df is not None and not df.empty:
            logger.info(f"获取现金流量表数据成功: {ts_code}，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_financial_indicator(self, ts_code: str, period: str = None,
                                 start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取财务指标数据

        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame包含: eps, roe, roa, debt_to_assets, current_ratio等
        """
        params = {'ts_code': ts_code}
        if period:
            params['period'] = period
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        df = self.pro.fina_indicator(**params)

        if df is not None and not df.empty:
            logger.info(f"获取财务指标数据成功: {ts_code}，共{len(df)}条")
        return df

    # ==================== 行业数据 ====================

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_industry_index_list(self, src: str = 'SW2021') -> pd.DataFrame:
        """
        获取行业指数列表

        Args:
            src: 指数来源 SW2021-申万2021, SW-申万, CSI-中证

        Returns:
            DataFrame包含: index_code, index_name, industry_name等
        """
        df = self.pro.index_classify(level='L1', src=src)

        if df is not None and not df.empty:
            logger.info(f"获取行业指数列表成功，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_industry_index_daily(self, ts_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        获取行业指数日线行情

        Args:
            ts_code: 指数代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD

        Returns:
            DataFrame包含: ts_code, trade_date, close, pct_chg, vol, amount等
        """
        params = {
            'ts_code': ts_code,
            'start_date': start_date
        }
        if end_date:
            params['end_date'] = end_date

        df = self.pro.index_daily(**params)

        if df is not None and not df.empty:
            logger.info(f"获取行业指数行情成功: {ts_code}，共{len(df)}条")
        return df

    @retry_on_error(max_retries=3)
    @rate_limit(calls_per_minute=200)
    def get_stock_industry(self, ts_code: str = None, src: str = 'SW2021') -> pd.DataFrame:
        """
        获取股票所属行业

        Args:
            ts_code: 股票代码
            src: 行业分类标准 SW2021-申万2021

        Returns:
            DataFrame包含: ts_code, industry_name, industry_code等
        """
        params = {'src': src}
        if ts_code:
            params['ts_code'] = ts_code

        df = self.pro.index_member(**params)

        if df is not None and not df.empty:
            logger.info(f"获取股票行业分类成功，共{len(df)}条")
        return df

    # ==================== 工具方法 ====================

    @staticmethod
    def convert_to_ts_code(code: str, market: str) -> str:
        """
        转换为Tushare格式代码

        Args:
            code: 股票代码 如 '600000'
            market: 市场 'SZ' 或 'SH'

        Returns:
            Tushare格式代码 如 '600000.SH'
        """
        return f"{code}.{market.upper()}"

    @staticmethod
    def convert_from_ts_code(ts_code: str) -> tuple:
        """
        从Tushare格式转换为普通格式

        Args:
            ts_code: Tushare格式代码 如 '600000.SH'

        Returns:
            (code, market) 如 ('600000', 'SH')
        """
        if '.' in ts_code:
            code, market = ts_code.split('.')
            return code, market
        return ts_code, None

    @staticmethod
    def date_to_tushare_format(date_str: str) -> str:
        """
        转换日期为Tushare格式

        Args:
            date_str: 日期字符串 '2025-01-04' 或 '20250104'

        Returns:
            Tushare格式日期 '20250104'
        """
        return date_str.replace('-', '')

    @staticmethod
    def tushare_date_to_normal(ts_date: str) -> str:
        """
        Tushare日期转普通格式

        Args:
            ts_date: Tushare日期 '20250104'

        Returns:
            普通格式日期 '2025-01-04'
        """
        if len(ts_date) == 8:
            return f"{ts_date[:4]}-{ts_date[4:6]}-{ts_date[6:8]}"
        return ts_date
