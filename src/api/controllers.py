"""API控制器 - 直接从Tushare获取数据"""
from flask import request, jsonify
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data_source.data_fetcher import DataFetcher
from src.utils.logger import logger


class IndustryController:
    """行业控制器"""

    def __init__(self):
        self.fetcher = DataFetcher()

    def get_industries(self):
        """获取所有行业列表"""
        try:
            industries = self.fetcher.fetch_industries()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': industries,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取行业列表失败: {e}")
            return jsonify({
                'code': 500,
                'message': str(e),
                'data': None
            }), 500

    def get_industry(self, code):
        """获取特定行业详情"""
        try:
            industries = self.fetcher.fetch_industries()
            industry = next((ind for ind in industries if ind.get('code') == code), None)

            if not industry:
                return jsonify({
                    'code': 404,
                    'message': '行业不存在',
                    'data': None
                }), 404

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': industry,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取行业详情失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_industry_ranking(self):
        """获取行业排名"""
        try:
            industries = self.fetcher.fetch_industries()
            # 按涨跌幅排序
            sorted_industries = sorted(
                industries,
                key=lambda x: x.get('price_change', 0),
                reverse=True
            )[:20]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': sorted_industries,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取行业排名失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500


class StockController:
    """股票控制器"""

    def __init__(self):
        self.fetcher = DataFetcher()

    def get_stocks(self):
        """获取股票列表"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            market = request.args.get('market', None)

            # 从Tushare获取股票列表
            stocks = self.fetcher.fetch_stocks(market=market)
            total = len(stocks)

            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            paginated_stocks = stocks[start:end]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'items': paginated_stocks,
                    'total': total,
                    'page': page,
                    'per_page': per_page
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_stock(self, code):
        """获取股票详情"""
        try:
            # 获取基本信息
            stocks = self.fetcher.fetch_stocks()
            stock = next((s for s in stocks if s.get('code') == code), None)

            if not stock:
                return jsonify({'code': 404, 'message': '股票不存在'}), 404

            # 获取日线数据
            try:
                daily_data = self.fetcher.fetch_daily_data(code)
                if daily_data:
                    latest = daily_data[0] if isinstance(daily_data, list) and daily_data else daily_data
                    stock.update({
                        'price': latest.get('close'),
                        'price_change': latest.get('pct_chg'),
                        'volume': latest.get('vol'),
                        'amount': latest.get('amount'),
                        'trade_date': latest.get('trade_date')
                    })
            except Exception as de:
                logger.warning(f"获取日线数据失败: {de}")

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': stock,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取股票详情失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_financial(self, code):
        """获取财务数据"""
        try:
            financial_data = self.fetcher.fetch_financial_data(code)

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': financial_data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取财务数据失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_valuation(self, code):
        """获取估值分析"""
        try:
            # 获取财务数据用于估值分析
            financial_data = self.fetcher.fetch_financial_data(code)
            daily_data = self.fetcher.fetch_daily_data(code)

            if not financial_data or not daily_data:
                return jsonify({'code': 404, 'message': '暂无估值数据'}), 404

            # 简单的估值分析
            latest_financial = financial_data[0] if isinstance(financial_data, list) and financial_data else financial_data
            latest_daily = daily_data[0] if isinstance(daily_data, list) and daily_data else daily_data

            valuation = {
                'stock_code': code,
                'current_price': latest_daily.get('close'),
                'pe_ratio': latest_financial.get('pe'),
                'pb_ratio': latest_financial.get('pb'),
                'roe': latest_financial.get('roe'),
                'analysis_date': datetime.now().isoformat()
            }

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': valuation,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取估值分析失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def filter_stocks(self):
        """筛选股票"""
        try:
            filters = request.json or {}
            stocks = self.fetcher.fetch_stocks()

            # TODO: 实现更复杂的筛选逻辑
            filtered = stocks

            if 'market' in filters:
                market = filters['market'].upper()
                filtered = [s for s in filtered if s.get('market') == market]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': filtered[:100]  # 限制返回数量
            })
        except Exception as e:
            logger.error(f"筛选股票失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500


class AnalysisController:
    """分析控制器"""

    def __init__(self):
        self.fetcher = DataFetcher()

    def get_recommendations(self):
        """获取推荐股票列表"""
        try:
            top_n = request.args.get('top_n', 10, type=int)

            # 获取所有股票
            stocks = self.fetcher.fetch_stocks()

            # TODO: 实现基于Tushare数据的推荐算法
            # 目前返回前N个股票
            recommendations = stocks[:top_n]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': recommendations,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取推荐列表失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_graham_analysis(self, code):
        """获取格雷厄姆分析结果"""
        try:
            # 获取必要的数据
            financial_data = self.fetcher.fetch_financial_data(code)
            daily_data = self.fetcher.fetch_daily_data(code)

            if not financial_data or not daily_data:
                return jsonify({'code': 404, 'message': '暂无分析数据'}), 404

            # 简化的格雷厄姆分析
            latest_financial = financial_data[0] if isinstance(financial_data, list) and financial_data else financial_data
            latest_daily = daily_data[0] if isinstance(daily_data, list) and daily_data else daily_data

            analysis = {
                'stock_code': code,
                'current_price': latest_daily.get('close'),
                'pe_ratio': latest_financial.get('pe'),
                'pb_ratio': latest_financial.get('pb'),
                'roe': latest_financial.get('roe'),
                'graham_score': 0,  # TODO: 实现评分算法
                'analysis_date': datetime.now().isoformat()
            }

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': analysis,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"获取格雷厄姆分析失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500


class TaskController:
    """任务控制器"""

    def trigger_crawl(self):
        """触发数据更新任务（已废弃，保留接口兼容性）"""
        try:
            return jsonify({
                'code': 200,
                'message': '系统已改为实时获取数据，无需手动触发',
                'data': {'status': 'deprecated'}
            })
        except Exception as e:
            logger.error(f"触发任务失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500

    def get_task_status(self, task_id):
        """获取任务状态（已废弃，保留接口兼容性）"""
        try:
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'task_id': task_id, 'status': 'deprecated'}
            })
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return jsonify({'code': 500, 'message': str(e)}), 500


# 创建控制器实例
industry_controller = IndustryController()
stock_controller = StockController()
analysis_controller = AnalysisController()
task_controller = TaskController()
