"""API路由定义"""
from flask import Blueprint
from .controllers import (
    industry_controller,
    stock_controller,
    analysis_controller,
    task_controller
)


def register_routes(app):
    """注册所有路由"""
    api_prefix = '/api/v1'

    # 行业相关路由
    industry_bp = Blueprint('industry', __name__)
    industry_bp.add_url_rule('/industries', 'get_industries', industry_controller.get_industries, methods=['GET'])
    industry_bp.add_url_rule('/industries/<code>', 'get_industry', industry_controller.get_industry, methods=['GET'])
    industry_bp.add_url_rule('/industries/ranking', 'get_industry_ranking', industry_controller.get_industry_ranking, methods=['GET'])

    # 股票相关路由
    stock_bp = Blueprint('stock', __name__)
    stock_bp.add_url_rule('/stocks', 'get_stocks', stock_controller.get_stocks, methods=['GET'])
    stock_bp.add_url_rule('/stocks/<code>', 'get_stock', stock_controller.get_stock, methods=['GET'])
    stock_bp.add_url_rule('/stocks/<code>/financial', 'get_financial', stock_controller.get_financial, methods=['GET'])
    stock_bp.add_url_rule('/stocks/<code>/valuation', 'get_valuation', stock_controller.get_valuation, methods=['GET'])
    stock_bp.add_url_rule('/stocks/filter', 'filter_stocks', stock_controller.filter_stocks, methods=['POST'])

    # 分析相关路由
    analysis_bp = Blueprint('analysis', __name__)
    analysis_bp.add_url_rule('/analysis/recommendations', 'get_recommendations', analysis_controller.get_recommendations, methods=['GET'])
    analysis_bp.add_url_rule('/analysis/graham/<code>', 'get_graham_analysis', analysis_controller.get_graham_analysis, methods=['GET'])

    # 任务相关路由
    task_bp = Blueprint('task', __name__)
    task_bp.add_url_rule('/tasks/crawl/trigger', 'trigger_crawl', task_controller.trigger_crawl, methods=['POST'])
    task_bp.add_url_rule('/tasks/status/<task_id>', 'get_task_status', task_controller.get_task_status, methods=['GET'])

    # 注册蓝图
    app.register_blueprint(industry_bp, url_prefix=api_prefix)
    app.register_blueprint(stock_bp, url_prefix=api_prefix)
    app.register_blueprint(analysis_bp, url_prefix=api_prefix)
    app.register_blueprint(task_bp, url_prefix=api_prefix)

    # 健康检查
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}

    @app.route('/')
    def index():
        return {
            'name': 'Graham Value Investment Analyzer API',
            'version': '1.0.0',
            'endpoints': {
                'industries': f'{api_prefix}/industries',
                'stocks': f'{api_prefix}/stocks',
                'analysis': f'{api_prefix}/analysis',
                'tasks': f'{api_prefix}/tasks'
            }
        }
