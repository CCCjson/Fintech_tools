"""行业分析模块"""
from typing import Dict, Any, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger


class IndustryAnalyzer:
    """行业分析器"""

    def __init__(self):
        self.logger = logger

    def analyze_industry_valuation(self, industries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        行业估值分析

        Args:
            industries: 行业数据列表

        Returns:
            分析结果
        """
        if not industries:
            return {}

        # 计算平均估值
        total_pe = sum(ind.get('pe_ratio', 0) for ind in industries if ind.get('pe_ratio', 0) > 0)
        total_pb = sum(ind.get('pb_ratio', 0) for ind in industries if ind.get('pb_ratio', 0) > 0)
        count = len([ind for ind in industries if ind.get('pe_ratio', 0) > 0])

        avg_pe = total_pe / count if count > 0 else 0
        avg_pb = total_pb / count if count > 0 else 0

        # 找出低估和高估行业
        undervalued = []
        overvalued = []

        for industry in industries:
            pe = industry.get('pe_ratio', 0)
            if pe > 0:
                if pe < avg_pe * 0.8:
                    undervalued.append(industry)
                elif pe > avg_pe * 1.2:
                    overvalued.append(industry)

        return {
            'average_pe': avg_pe,
            'average_pb': avg_pb,
            'undervalued_industries': undervalued[:10],  # 前10个低估行业
            'overvalued_industries': overvalued[:10]  # 前10个高估行业
        }

    def rank_industries(self, industries: List[Dict[str, Any]],
                        by: str = 'price_change') -> List[Dict[str, Any]]:
        """
        行业排名

        Args:
            industries: 行业数据列表
            by: 排名依据 ('price_change', 'turnover', 'pe_ratio')

        Returns:
            排名后的行业列表
        """
        return sorted(industries, key=lambda x: x.get(by, 0), reverse=True)

    def identify_hot_industries(self, industries: List[Dict[str, Any]],
                                 top_n: int = 10) -> List[Dict[str, Any]]:
        """
        识别热门行业

        Args:
            industries: 行业数据列表
            top_n: 返回前N个

        Returns:
            热门行业列表
        """
        # 综合考虑涨跌幅和成交额
        scored_industries = []

        for industry in industries:
            price_change = industry.get('price_change', 0)
            turnover = industry.get('turnover', 0)

            # 简单评分：涨跌幅权重60%，成交额权重40%
            score = price_change * 0.6 + (turnover / 1e10) * 0.4

            scored_industries.append({
                **industry,
                'hot_score': score
            })

        # 按评分排序
        scored_industries.sort(key=lambda x: x['hot_score'], reverse=True)

        return scored_industries[:top_n]
