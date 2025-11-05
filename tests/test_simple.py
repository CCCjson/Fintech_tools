"""简单测试脚本（不使用Selenium）"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import logger
import requests


def test_connection():
    """测试网络连接"""
    logger.info("=" * 60)
    logger.info("简单连接测试（不使用Selenium）")
    logger.info("=" * 60)

    test_cases = [
        {
            'name': '测试百度',
            'url': 'https://www.baidu.com',
            'expected': 200
        },
        {
            'name': '测试东方财富首页',
            'url': 'https://www.eastmoney.com',
            'expected': 200
        },
        {
            'name': '测试东方财富行情中心',
            'url': 'https://quote.eastmoney.com',
            'expected': 200
        }
    ]

    results = []

    for test in test_cases:
        logger.info(f"\n{test['name']}")
        logger.info(f"URL: {test['url']}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }

            response = requests.get(
                test['url'],
                headers=headers,
                timeout=10,
                allow_redirects=True
            )

            status_code = response.status_code
            content_length = len(response.content)

            logger.info(f"状态码: {status_code}")
            logger.info(f"响应大小: {content_length} bytes")
            logger.info(f"响应时间: {response.elapsed.total_seconds():.2f}秒")

            if status_code == test['expected']:
                logger.info("✅ 测试通过")
                results.append(True)
            else:
                logger.warning(f"⚠️ 状态码不符合预期 (期望:{test['expected']}, 实际:{status_code})")
                results.append(False)

            # 检查是否被重定向或返回验证页面
            if 'verify' in response.url.lower() or 'captcha' in response.url.lower():
                logger.warning("⚠️ 可能触发了验证码验证")

        except requests.exceptions.Timeout:
            logger.error("❌ 请求超时")
            results.append(False)
        except requests.exceptions.ConnectionError:
            logger.error("❌ 连接失败")
            results.append(False)
        except Exception as e:
            logger.error(f"❌ 错误: {e}")
            results.append(False)

    # 总结
    logger.info("\n" + "=" * 60)
    success_count = sum(results)
    total_count = len(results)
    logger.info(f"测试总结: {success_count}/{total_count} 通过")

    if success_count == total_count:
        logger.info("✅ 所有测试通过，网络访问正常")
    elif success_count > 0:
        logger.warning("⚠️ 部分测试失败，可能存在网络问题")
    else:
        logger.error("❌ 所有测试失败，请检查网络连接")

    logger.info("=" * 60)

    return success_count == total_count


if __name__ == '__main__':
    test_connection()
