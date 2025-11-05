"""格雷厄姆价值投资算法实现"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import config
from src.utils.logger import logger


class GrahamAnalyzer:
    """格雷厄姆价值投资分析器"""

    def __init__(self):
        self.config = config
        self.logger = logger
        self.graham_config = config.graham

    def calculate_intrinsic_value(self, eps: float, growth_rate: float = 0.05,
                                   method: str = 'simplified') -> float:
        """
        计算内在价值

        Args:
            eps: 每股收益
            growth_rate: 预期年增长率（默认5%）
            method: 计算方法 ('simplified', 'asset_based', 'earnings_based')

        Returns:
            内在价值
        """
        if method == 'simplified':
            return self._simplified_graham_formula(eps, growth_rate)
        elif method == 'asset_based':
            return self._asset_based_value(eps)
        elif method == 'earnings_based':
            return self._earnings_based_value(eps, growth_rate)
        else:
            return self._simplified_graham_formula(eps, growth_rate)

    def _simplified_graham_formula(self, eps: float, growth_rate: float) -> float:
        """
        简化的格雷厄姆公式
        内在价值 = (EPS × (8.5 + 2g)) × 4.4 / Y

        Args:
            eps: 每股收益
            growth_rate: 预期年增长率（小数形式，如0.05表示5%）

        Returns:
            内在价值
        """
        if eps <= 0:
            return 0

        # 将增长率转换为百分比
        g = growth_rate * 100

        # AAA公司债收益率
        Y = self.graham_config.get('aaa_bond_yield', 0.044)

        # 格雷厄姆公式
        intrinsic_value = (eps * (8.5 + 2 * g)) * 4.4 / Y

        return max(0, intrinsic_value)

    def _asset_based_value(self, bvps: float) -> float:
        """
        基于净资产的价值
        适用于资产型公司

        Args:
            bvps: 每股净资产

        Returns:
            内在价值
        """
        # 简化版：使用净资产
        return bvps * 1.2  # 给予20%的溢价

    def _earnings_based_value(self, eps: float, growth_rate: float) -> float:
        """
        基于盈利能力的价值

        Args:
            eps: 每股收益
            growth_rate: 增长率

        Returns:
            内在价值
        """
        if eps <= 0:
            return 0

        # 根据增长率确定合理市盈率
        reasonable_pe = 15 + growth_rate * 100

        return eps * reasonable_pe

    def calculate_safety_margin(self, intrinsic_value: float, current_price: float) -> float:
        """
        计算安全边际

        Args:
            intrinsic_value: 内在价值
            current_price: 当前价格

        Returns:
            安全边际（百分比）
        """
        if intrinsic_value <= 0:
            return -100

        safety_margin = ((intrinsic_value - current_price) / intrinsic_value) * 100

        return safety_margin

    def preliminary_filter(self, stock_data: Dict[str, Any]) -> bool:
        """
        初步筛选

        Args:
            stock_data: 股票数据

        Returns:
            是否通过筛选
        """
        filter_config = self.graham_config.get('filter', {})

        # 获取筛选标准
        min_market_cap = filter_config.get('min_market_cap', 500000000)
        max_pe_ratio = filter_config.get('max_pe_ratio', 25)
        max_pb_ratio = filter_config.get('max_pb_ratio', 3)
        min_roe = filter_config.get('min_roe', 0.1)
        max_debt_ratio = filter_config.get('max_debt_ratio', 0.6)

        # 进行筛选
        checks = [
            stock_data.get('total_market_cap', 0) >= min_market_cap,
            0 < stock_data.get('pe_ratio', 0) <= max_pe_ratio,
            0 < stock_data.get('pb_ratio', 0) <= max_pb_ratio,
            stock_data.get('roe', 0) >= min_roe,
            0 <= stock_data.get('debt_ratio', 1) <= max_debt_ratio,
            stock_data.get('eps', 0) > 0,  # 必须盈利
        ]

        return all(checks)

    def calculate_graham_score(self, stock_data: Dict[str, Any],
                                 safety_margin: float) -> Tuple[float, Dict[str, float]]:
        """
        计算格雷厄姆综合评分

        Args:
            stock_data: 股票数据
            safety_margin: 安全边际

        Returns:
            (总分, 各项评分详情)
        """
        scores = {
            'financial_health': self._score_financial_health(stock_data),
            'profitability': self._score_profitability(stock_data),
            'valuation': self._score_valuation(stock_data),
            'safety_margin': self._score_safety_margin(safety_margin)
        }

        total_score = sum(scores.values())

        return total_score, scores

    def _score_financial_health(self, stock_data: Dict[str, Any]) -> float:
        """
        财务健康度评分 (0-25分)

        Args:
            stock_data: 股票数据

        Returns:
            评分
        """
        score = 0

        # 流动比率 (5分)
        current_ratio = stock_data.get('current_ratio', 0)
        if current_ratio >= 2:
            score += 5
        elif current_ratio >= 1.5:
            score += 3
        elif current_ratio >= 1:
            score += 1

        # 速动比率 (5分)
        quick_ratio = stock_data.get('quick_ratio', 0)
        if quick_ratio >= 1:
            score += 5
        elif quick_ratio >= 0.8:
            score += 3

        # 资产负债率 (5分)
        debt_ratio = stock_data.get('debt_ratio', 1)
        if debt_ratio <= 0.3:
            score += 5
        elif debt_ratio <= 0.5:
            score += 3
        elif debt_ratio <= 0.6:
            score += 1

        # 经营现金流 (5分)
        operating_cash_flow = stock_data.get('operating_cash_flow', 0)
        net_profit = stock_data.get('net_profit', 1)
        if operating_cash_flow > 0 and net_profit > 0:
            cash_flow_ratio = operating_cash_flow / net_profit
            if cash_flow_ratio >= 1.2:
                score += 5
            elif cash_flow_ratio >= 0.8:
                score += 3

        # 利息保障倍数 (5分) - 简化处理
        if debt_ratio < 0.3:
            score += 5
        elif debt_ratio < 0.5:
            score += 3

        return min(25, score)

    def _score_profitability(self, stock_data: Dict[str, Any]) -> float:
        """
        盈利能力评分 (0-25分)

        Args:
            stock_data: 股票数据

        Returns:
            评分
        """
        score = 0

        # ROE (8分)
        roe = stock_data.get('roe', 0)
        if roe >= 0.2:  # 20%
            score += 8
        elif roe >= 0.15:  # 15%
            score += 6
        elif roe >= 0.1:  # 10%
            score += 4

        # 净利率 (8分)
        net_margin = stock_data.get('net_margin', 0)
        if net_margin >= 0.15:  # 15%
            score += 8
        elif net_margin >= 0.1:  # 10%
            score += 6
        elif net_margin >= 0.05:  # 5%
            score += 3

        # 毛利率 (5分)
        gross_margin = stock_data.get('gross_margin', 0)
        if gross_margin >= 0.4:  # 40%
            score += 5
        elif gross_margin >= 0.3:  # 30%
            score += 3

        # 利润增长稳定性 (4分) - 简化处理
        net_profit_yoy = stock_data.get('net_profit_yoy', 0)
        if net_profit_yoy > 0:
            if net_profit_yoy >= 0.2:  # 20%
                score += 4
            elif net_profit_yoy >= 0.1:  # 10%
                score += 3
            elif net_profit_yoy >= 0:
                score += 2

        return min(25, score)

    def _score_valuation(self, stock_data: Dict[str, Any]) -> float:
        """
        估值水平评分 (0-25分)

        Args:
            stock_data: 股票数据

        Returns:
            评分
        """
        score = 0

        pe_ratio = stock_data.get('pe_ratio', 999)
        pb_ratio = stock_data.get('pb_ratio', 999)

        # PE估值 (8分)
        if pe_ratio > 0:
            if pe_ratio <= 10:
                score += 8
            elif pe_ratio <= 15:
                score += 6
            elif pe_ratio <= 20:
                score += 4
            elif pe_ratio <= 25:
                score += 2

        # PB估值 (8分)
        if pb_ratio > 0:
            if pb_ratio <= 1:
                score += 8
            elif pb_ratio <= 1.5:
                score += 6
            elif pb_ratio <= 2:
                score += 4
            elif pb_ratio <= 3:
                score += 2

        # PEG比率 (9分)
        eps = stock_data.get('eps', 0)
        net_profit_yoy = stock_data.get('net_profit_yoy', 0)

        if eps > 0 and net_profit_yoy > 0 and pe_ratio > 0:
            peg = pe_ratio / (net_profit_yoy * 100)
            if peg <= 0.8:
                score += 9
            elif peg <= 1:
                score += 7
            elif peg <= 1.5:
                score += 4

        return min(25, score)

    def _score_safety_margin(self, safety_margin: float) -> float:
        """
        安全边际评分 (0-25分)

        Args:
            safety_margin: 安全边际百分比

        Returns:
            评分
        """
        if safety_margin >= 50:
            return 25
        elif safety_margin >= 40:
            return 20
        elif safety_margin >= 30:
            return 15
        elif safety_margin >= 20:
            return 10
        elif safety_margin >= 10:
            return 5
        else:
            return 0

    def get_recommendation(self, total_score: float, safety_margin: float) -> str:
        """
        获取投资建议

        Args:
            total_score: 总分
            safety_margin: 安全边际

        Returns:
            投资建议
        """
        if total_score >= 90 and safety_margin >= 30:
            return "强烈推荐"
        elif total_score >= 75 and safety_margin >= 20:
            return "推荐"
        elif total_score >= 60 and safety_margin >= 10:
            return "可考虑"
        else:
            return "不推荐"

    def analyze(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        综合分析

        Args:
            stock_data: 股票数据

        Returns:
            分析结果
        """
        result = {
            'stock_code': stock_data.get('code', ''),
            'stock_name': stock_data.get('name', ''),
            'pass_filter': False,
            'intrinsic_value': 0,
            'current_price': stock_data.get('current_price', 0),
            'safety_margin': -100,
            'graham_score': 0,
            'score_details': {},
            'recommendation': '不推荐',
            'risk_level': '高',
            'analysis_date': datetime.now().date()
        }

        # 初步筛选
        if not self.preliminary_filter(stock_data):
            self.logger.info(f"股票 {stock_data.get('code')} 未通过初步筛选")
            return result

        result['pass_filter'] = True

        # 计算内在价值
        eps = stock_data.get('eps', 0)
        growth_rate = stock_data.get('net_profit_yoy', 0.05)
        intrinsic_value = self.calculate_intrinsic_value(eps, growth_rate)
        result['intrinsic_value'] = intrinsic_value

        # 计算安全边际
        current_price = stock_data.get('current_price', 0)
        safety_margin = self.calculate_safety_margin(intrinsic_value, current_price)
        result['safety_margin'] = safety_margin

        # 计算格雷厄姆评分
        total_score, score_details = self.calculate_graham_score(stock_data, safety_margin)
        result['graham_score'] = total_score
        result['score_details'] = score_details

        # 获取投资建议
        recommendation = self.get_recommendation(total_score, safety_margin)
        result['recommendation'] = recommendation

        # 风险评估
        if total_score >= 75:
            result['risk_level'] = '低'
        elif total_score >= 60:
            result['risk_level'] = '中'
        else:
            result['risk_level'] = '高'

        return result
