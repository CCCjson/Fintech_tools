"""主启动文件"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.api.app import create_app
from src.utils.config import config
from src.utils.logger import logger


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Graham Value Investment Analyzer 启动中...")
    logger.info("=" * 60)

    try:
        # 创建Flask应用
        logger.info("创建Flask应用...")
        app = create_app()

        # 获取配置
        host = config.get('app.host', '0.0.0.0')
        port = config.get('app.port', 5000)
        debug = config.get('app.debug', False)

        logger.info(f"Flask服务配置: {host}:{port}")
        logger.info("=" * 60)
        logger.info("应用启动成功！")
        logger.info(f"API地址: http://{host}:{port}")
        logger.info(f"API文档: http://{host}:{port}/")
        logger.info("=" * 60)
        logger.info("说明: 系统已改为实时调用Tushare API获取数据")
        logger.info("=" * 60)

        # 启动Flask服务
        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        logger.info("应用已关闭")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise


if __name__ == '__main__':
    main()
