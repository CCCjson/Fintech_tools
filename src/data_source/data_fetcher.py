"""数据获取统一接口 - 将Tushare数据转换为字典格式"""
from typing import List, Optional
from datetime import datetime, date
import pandas as pd

from src.data_source.tushare_api import TushareClient
from src.utils.logger import logger


class DataFetcher:
    """数据获取统一接口"""

    def __init__(self, tushare_client: TushareClient = None):
        """
        初始化DataFetcher

        Args:
            tushare_client: TushareClient实例，如果不提供则创建新实例
        """
        self.ts_client = tushare_client or TushareClient()
        logger.info("DataFetcher初始化成功")

    # ==================== 股票基础数据 ====================

    def fetch_stocks(self, market: str = None) -> List[dict]:
        """
        获取股票列表

        Args:
            market: 市场类型 ('SZ', 'SH', None表示全部)

        Returns:
            股票数据字典列表
        """
        logger.info(f"开始获取股票列表，市场: {market or '全部'}")

        # 获取Tushare数据
        df = self.ts_client.get_stock_list(market=market)

        if df is None or df.empty:
            logger.warning("未获取到股票数据")
            return []

        # 转换为系统格式
        stocks = []
        for _, row in df.iterrows():
            try:
                # 转换股票代码格式
                code, market_code = self.ts_client.convert_from_ts_code(row['ts_code'])

                stock_data = {
                    'code': code,
                    'name': row.get('name', ''),
                    'market': market_code,
                    'industry_code': row.get('industry', ''),  # 暂时使用industry字段
                    'list_date': self._parse_date(row.get('list_date')),
                    # Tushare没有直接提供股本数据，需要额外获取
                    'total_shares': None,
                    'circulating_shares': None
                }
                stocks.append(stock_data)

            except Exception as e:
                logger.warning(f"转换股票数据失败: {row.get('ts_code')}, 错误: {e}")
                continue

        logger.info(f"获取股票列表成功，共{len(stocks)}条")
        return stocks

    # ==================== 日线行情数据 ====================

    def fetch_daily_data(self, stock_codes: List[str] = None, trade_date: str = None) -> List[dict]:
        """
        获取日线行情数据

        Args:
            stock_codes: 股票代码列表 ['600000', '000001']，None表示全市场
            trade_date: 交易日期 '2025-01-04' 或 '20250104'

        Returns:
            日线行情数据字典列表
        """
        logger.info(f"开始获取日线行情数据，日期: {trade_date}")

        # 转换日期格式
        if trade_date:
            trade_date = self.ts_client.date_to_tushare_format(trade_date)

        # 获取行情数据
        daily_df = self.ts_client.get_daily_quotes(trade_date=trade_date)
        # 获取指标数据
        basic_df = self.ts_client.get_daily_basic(trade_date=trade_date)

        if daily_df is None or daily_df.empty:
            logger.warning("未获取到日线行情数据")
            return []

        # 合并数据
        if basic_df is not None and not basic_df.empty:
            merged_df = pd.merge(daily_df, basic_df, on=['ts_code', 'trade_date'], how='left')
        else:
            merged_df = daily_df

        # 转换为系统格式
        daily_data_list = []
        for _, row in merged_df.iterrows():
            try:
                code, market = self.ts_client.convert_from_ts_code(row['ts_code'])

                # 如果指定了股票代码列表，进行过滤
                if stock_codes and code not in stock_codes:
                    continue

                daily_data = {
                    'stock_code': code,
                    'trade_date': self._parse_date(row.get('trade_date')),
                    'open': self._safe_float(row.get('open')),
                    'high': self._safe_float(row.get('high')),
                    'low': self._safe_float(row.get('low')),
                    'close': self._safe_float(row.get('close')),
                    'volume': self._safe_float(row.get('vol')) * 100 if row.get('vol') else None,  # Tushare单位是手，转为股
                    'turnover': self._safe_float(row.get('amount')) * 1000 if row.get('amount') else None,  # Tushare单位是千元，转为元
                    'change_percent': self._safe_float(row.get('pct_chg')),
                    'change_amount': self._safe_float(row.get('change')),
                    'amplitude': None,  # Tushare没有直接提供，可以计算
                    'turnover_rate': self._safe_float(row.get('turnover_rate')),
                    'volume_ratio': None,  # 需要额外计算
                    'pe_ratio': self._safe_float(row.get('pe')),
                    'pb_ratio': self._safe_float(row.get('pb')),
                    'total_market_cap': self._safe_float(row.get('total_mv')) * 10000 if row.get('total_mv') else None,  # 万元转元
                    'circulating_market_cap': self._safe_float(row.get('circ_mv')) * 10000 if row.get('circ_mv') else None
                }

                # 计算振幅
                if daily_data['high'] and daily_data['low'] and row.get('pre_close'):
                    pre_close = self._safe_float(row.get('pre_close'))
                    if pre_close and pre_close > 0:
                        daily_data['amplitude'] = ((daily_data['high'] - daily_data['low']) / pre_close) * 100

                daily_data_list.append(daily_data)

            except Exception as e:
                logger.warning(f"转换日线数据失败: {row.get('ts_code')}, 错误: {e}")
                continue

        logger.info(f"获取日线行情成功，共{len(daily_data_list)}条")
        return daily_data_list

    # ==================== 财务数据 ====================

    def fetch_financial_data(self, stock_code: str, market: str = 'SH', period: str = None) -> Optional[dict]:
        """
        获取财务数据

        Args:
            stock_code: 股票代码 '600000'
            market: 市场 'SH' 或 'SZ'
            period: 报告期 '20231231'，None表示最新

        Returns:
            财务数据字典
        """
        logger.info(f"开始获取财务数据: {stock_code}")

        ts_code = self.ts_client.convert_to_ts_code(stock_code, market)

        try:
            # 获取各类财务数据
            income_df = self.ts_client.get_income_statement(ts_code, period=period)
            balance_df = self.ts_client.get_balance_sheet(ts_code, period=period)
            cashflow_df = self.ts_client.get_cash_flow(ts_code, period=period)
            indicator_df = self.ts_client.get_financial_indicator(ts_code, period=period)

            # 取最新一期数据
            income_row = income_df.iloc[0] if income_df is not None and not income_df.empty else None
            balance_row = balance_df.iloc[0] if balance_df is not None and not balance_df.empty else None
            cashflow_row = cashflow_df.iloc[0] if cashflow_df is not None and not cashflow_df.empty else None
            indicator_row = indicator_df.iloc[0] if indicator_df is not None and not indicator_df.empty else None

            if income_row is None and balance_row is None and indicator_row is None:
                logger.warning(f"未获取到财务数据: {stock_code}")
                return None

            # 合并数据
            financial_data = {
                'stock_code': stock_code,
                'report_date': self._parse_date(
                    income_row.get('end_date') if income_row is not None else
                    balance_row.get('end_date') if balance_row is not None else
                    indicator_row.get('end_date')
                ),

                # 利润表数据
                'total_revenue': self._safe_float(income_row.get('total_revenue') if income_row is not None else None),
                'revenue_yoy': self._safe_float(income_row.get('revenue_yoy') if income_row is not None else None),
                'net_profit': self._safe_float(income_row.get('n_income') if income_row is not None else None),
                'net_profit_yoy': self._safe_float(income_row.get('n_income_yoy') if income_row is not None else None),

                # 财务指标
                'eps': self._safe_float(indicator_row.get('eps') if indicator_row is not None else None),
                'gross_margin': self._safe_float(indicator_row.get('grossprofit_margin') if indicator_row is not None else None),
                'net_margin': self._safe_float(indicator_row.get('netprofit_margin') if indicator_row is not None else None),

                # 资产负债表数据
                'total_assets': self._safe_float(balance_row.get('total_assets') if balance_row is not None else None),
                'total_liabilities': self._safe_float(balance_row.get('total_liab') if balance_row is not None else None),
                'net_assets': self._safe_float(balance_row.get('total_hldr_eqy_exc_min_int') if balance_row is not None else None),

                # 财务比率
                'debt_ratio': self._safe_float(indicator_row.get('debt_to_assets') if indicator_row is not None else None),
                'current_ratio': self._safe_float(indicator_row.get('current_ratio') if indicator_row is not None else None),
                'quick_ratio': self._safe_float(indicator_row.get('quick_ratio') if indicator_row is not None else None),

                # 现金流数据
                'operating_cash_flow': self._safe_float(cashflow_row.get('n_cashflow_act') if cashflow_row is not None else None),
                'investing_cash_flow': self._safe_float(cashflow_row.get('n_cashflow_inv_act') if cashflow_row is not None else None),
                'financing_cash_flow': self._safe_float(cashflow_row.get('n_cash_flows_fnc_act') if cashflow_row is not None else None),

                # 重要指标
                'roe': self._safe_float(indicator_row.get('roe') if indicator_row is not None else None),
                'roa': self._safe_float(indicator_row.get('roa') if indicator_row is not None else None),
                'bvps': self._safe_float(indicator_row.get('bps') if indicator_row is not None else None),
                'undistributed_profit_per_share': self._safe_float(indicator_row.get('undist_profit_ps') if indicator_row is not None else None)
            }

            logger.info(f"获取财务数据成功: {stock_code}")
            return financial_data

        except Exception as e:
            logger.error(f"获取财务数据失败: {stock_code}, 错误: {e}")
            return None

    # ==================== 行业数据 ====================

    def fetch_industries(self, trade_date: str = None) -> List[dict]:
        """
        获取行业数据

        Args:
            trade_date: 交易日期 '2025-01-04'

        Returns:
            行业数据字典列表
        """
        logger.info(f"开始获取行业数据，日期: {trade_date}")

        try:
            # 获取申万一级行业列表
            industry_list_df = self.ts_client.get_industry_index_list(src='SW2021')

            if industry_list_df is None or industry_list_df.empty:
                logger.warning("未获取到行业列表")
                return []

            # 转换日期格式
            if trade_date:
                ts_trade_date = self.ts_client.date_to_tushare_format(trade_date)
            else:
                ts_trade_date = datetime.now().strftime('%Y%m%d')

            industries = []

            # 获取每个行业的行情数据
            for _, row in industry_list_df.iterrows():
                try:
                    index_code = row.get('index_code')
                    industry_name = row.get('industry_name')

                    # 获取行业指数当日行情
                    index_daily_df = self.ts_client.get_industry_index_daily(
                        ts_code=index_code,
                        start_date=ts_trade_date,
                        end_date=ts_trade_date
                    )

                    if index_daily_df is None or index_daily_df.empty:
                        continue

                    daily_row = index_daily_df.iloc[0]

                    industry_data = {
                        'code': index_code,
                        'name': industry_name,
                        'price_change': self._safe_float(daily_row.get('pct_chg')),
                        'volume': self._safe_float(daily_row.get('vol')),
                        'turnover': self._safe_float(daily_row.get('amount')),
                        'pe_ratio': None,  # 行业指数没有PE数据，需要自行计算
                        'pb_ratio': None,  # 行业指数没有PB数据，需要自行计算
                        'stock_count': 0,  # 需要额外统计
                        'leading_stocks': '[]'
                    }

                    industries.append(industry_data)

                except Exception as e:
                    logger.warning(f"转换行业数据失败: {row.get('industry_name')}, 错误: {e}")
                    continue

            logger.info(f"获取行业数据成功，共{len(industries)}条")
            return industries

        except Exception as e:
            logger.error(f"获取行业数据失败: {e}")
            return []

    # ==================== 工具方法 ====================

    @staticmethod
    def _parse_date(date_str) -> Optional[date]:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串 '20250104' 或 datetime对象

        Returns:
            date对象
        """
        if date_str is None:
            return None

        if isinstance(date_str, date):
            return date_str

        if isinstance(date_str, datetime):
            return date_str.date()

        if isinstance(date_str, str):
            try:
                # Tushare格式 YYYYMMDD
                if len(date_str) == 8:
                    return datetime.strptime(date_str, '%Y%m%d').date()
                # 标准格式 YYYY-MM-DD
                elif '-' in date_str:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                pass

        return None

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """
        安全转换为float

        Args:
            value: 任意值

        Returns:
            float或None
        """
        if value is None or value == '' or pd.isna(value):
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """
        安全转换为int

        Args:
            value: 任意值

        Returns:
            int或None
        """
        if value is None or value == '' or pd.isna(value):
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None
