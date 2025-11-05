"""风险评估模块"""
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger


class RiskAssessor:
    """风险评估器"""

    def __init__(self):
        self.logger = logger

    def assess_risk(self, stock_data: Dict[str, Any],
                    financial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        综合风险评估

        Args:
            stock_data: 股票数据
            financial_data: 财务数据

        Returns:
            风险评估结果
        """
        risk_factors = {
            'valuation_risk': self._assess_valuation_risk(stock_data),
            'financial_risk': self._assess_financial_risk(financial_data or stock_data),
            'liquidity_risk': self._assess_liquidity_risk(stock_data),
            'volatility_risk': self._assess_volatility_risk(stock_data)
        }

        # 计算总体风险等级
        risk_score = sum(risk_factors.values()) / len(risk_factors)

        if risk_score <= 30:
            overall_risk = '低'
        elif risk_score <= 60:
            overall_risk = '中'
        else:
            overall_risk = '高'

        return {
            'overall_risk': overall_risk,
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }

    def _assess_valuation_risk(self, stock_data: Dict[str, Any]) -> float:
        """
        估值风险评估 (0-100)

        Args:
            stock_data: 股票数据

        Returns:
            风险分数（越高风险越大）
        """
        pe_ratio = stock_data.get('pe_ratio', 0)
        pb_ratio = stock_data.get('pb_ratio', 0)

        risk_score = 0

        # PE风险
        if pe_ratio > 50:
            risk_score += 50
        elif pe_ratio > 30:
            risk_score += 30
        elif pe_ratio > 20:
            risk_score += 15

        # PB风险
        if pb_ratio > 5:
            risk_score += 50
        elif pb_ratio > 3:
            risk_score += 30
        elif pb_ratio > 2:
            risk_score += 15

        return min(100, risk_score)

    def _assess_financial_risk(self, financial_data: Dict[str, Any]) -> float:
        """
        财务风险评估 (0-100)

        Args:
            financial_data: 财务数据

        Returns:
            风险分数
        """
        debt_ratio = financial_data.get('debt_ratio', 0)
        current_ratio = financial_data.get('current_ratio', 0)
        roe = financial_data.get('roe', 0)

        risk_score = 0

        # 负债风险
        if debt_ratio > 0.7:
            risk_score += 40
        elif debt_ratio > 0.6:
            risk_score += 25

        # 流动性风险
        if current_ratio < 1:
            risk_score += 30
        elif current_ratio < 1.5:
            risk_score += 15

        # 盈利能力风险
        if roe < 0:
            risk_score += 30
        elif roe < 0.05:
            risk_score += 20

        return min(100, risk_score)

    def _assess_liquidity_risk(self, stock_data: Dict[str, Any]) -> float:
        """
        流动性风险评估 (0-100)

        Args:
            stock_data: 股票数据

        Returns:
            风险分数
        """
        turnover_rate = stock_data.get('turnover_rate', 0)
        circulating_market_cap = stock_data.get('circulating_market_cap', 0)

        risk_score = 0

        # 换手率风险
        if turnover_rate < 0.5:
            risk_score += 30
        elif turnover_rate < 1:
            risk_score += 15

        # 流通市值风险
        if circulating_market_cap < 1e9:  # 10亿
            risk_score += 40
        elif circulating_market_cap < 5e9:  # 50亿
            risk_score += 20

        return min(100, risk_score)

    def _assess_volatility_risk(self, stock_data: Dict[str, Any]) -> float:
        """
        波动性风险评估 (0-100)

        Args:
            stock_data: 股票数据

        Returns:
            风险分数
        """
        amplitude = stock_data.get('amplitude', 0)

        risk_score = 0

        # 振幅风险
        if amplitude > 10:
            risk_score += 60
        elif amplitude > 5:
            risk_score += 30
        elif amplitude > 3:
            risk_score += 15

        return min(100, risk_score)
