"""财务分析模块"""
from typing import Dict, Any, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger


class FinancialAnalyzer:
    """财务分析器"""

    def __init__(self):
        self.logger = logger

    def analyze_profitability(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        盈利能力分析

        Args:
            financial_data: 财务数据

        Returns:
            分析结果
        """
        result = {
            'roe': financial_data.get('roe', 0),
            'roa': financial_data.get('roa', 0),
            'net_margin': financial_data.get('net_margin', 0),
            'gross_margin': financial_data.get('gross_margin', 0),
            'profitability_rating': ''
        }

        # 综合评级
        roe = result['roe']
        net_margin = result['net_margin']

        if roe >= 0.15 and net_margin >= 0.1:
            result['profitability_rating'] = '优秀'
        elif roe >= 0.1 and net_margin >= 0.05:
            result['profitability_rating'] = '良好'
        elif roe >= 0.05:
            result['profitability_rating'] = '一般'
        else:
            result['profitability_rating'] = '较差'

        return result

    def analyze_solvency(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        偿债能力分析

        Args:
            financial_data: 财务数据

        Returns:
            分析结果
        """
        result = {
            'current_ratio': financial_data.get('current_ratio', 0),
            'quick_ratio': financial_data.get('quick_ratio', 0),
            'debt_ratio': financial_data.get('debt_ratio', 0),
            'solvency_rating': ''
        }

        current_ratio = result['current_ratio']
        debt_ratio = result['debt_ratio']

        if current_ratio >= 2 and debt_ratio <= 0.4:
            result['solvency_rating'] = '优秀'
        elif current_ratio >= 1.5 and debt_ratio <= 0.6:
            result['solvency_rating'] = '良好'
        elif current_ratio >= 1:
            result['solvency_rating'] = '一般'
        else:
            result['solvency_rating'] = '较差'

        return result

    def analyze_growth(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        成长能力分析

        Args:
            financial_data: 财务数据

        Returns:
            分析结果
        """
        result = {
            'revenue_yoy': financial_data.get('revenue_yoy', 0),
            'net_profit_yoy': financial_data.get('net_profit_yoy', 0),
            'growth_rating': ''
        }

        revenue_yoy = result['revenue_yoy']
        net_profit_yoy = result['net_profit_yoy']

        if revenue_yoy >= 0.2 and net_profit_yoy >= 0.2:
            result['growth_rating'] = '高成长'
        elif revenue_yoy >= 0.1 and net_profit_yoy >= 0.1:
            result['growth_rating'] = '稳定成长'
        elif revenue_yoy >= 0:
            result['growth_rating'] = '低成长'
        else:
            result['growth_rating'] = '负增长'

        return result

    def comprehensive_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        综合财务分析

        Args:
            financial_data: 财务数据

        Returns:
            综合分析结果
        """
        return {
            'profitability': self.analyze_profitability(financial_data),
            'solvency': self.analyze_solvency(financial_data),
            'growth': self.analyze_growth(financial_data)
        }
