#!/usr/bin/env python
"""测试新架构 - 不使用数据库"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.data_source.data_fetcher import DataFetcher
from src.utils.logger import logger

def test_fetch():
    """测试数据获取"""
    try:
        logger.info("=" * 60)
        logger.info("测试新架构 - 直接调用Tushare API")
        logger.info("=" * 60)

        fetcher = DataFetcher()

        # 测试1: 获取少量股票
        logger.info("\n测试1: 获取深圳市场前5个股票...")
        stocks = fetcher.fetch_stocks(market='SZ')
        logger.info(f"✓ 获取成功！共 {len(stocks)} 只股票")
        if stocks:
            logger.info(f"示例: {stocks[0]}")

        # 测试2: 获取行业数据
        logger.info("\n测试2: 获取行业数据...")
        industries = fetcher.fetch_industries()
        logger.info(f"✓ 获取成功！共 {len(industries)} 个行业")
        if industries:
            logger.info(f"示例: {industries[0]}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ 所有测试通过！新架构工作正常")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_fetch()
    sys.exit(0 if success else 1)
