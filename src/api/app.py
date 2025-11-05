"""Flask应用主文件"""
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import config
from src.utils.logger import logger
from .routes import register_routes


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # 配置
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False

    # CORS配置
    cors_origins = config.get('api.cors_origins', ['*'])
    CORS(app, origins=cors_origins)

    # 注册路由
    register_routes(app)

    logger.info("Flask应用创建成功")

    return app


if __name__ == '__main__':
    app = create_app()
    host = config.get('app.host', '0.0.0.0')
    port = config.get('app.port', 5000)
    debug = config.get('app.debug', False)

    logger.info(f"启动Flask服务: {host}:{port}")
    app.run(host=host, port=port, debug=debug)
