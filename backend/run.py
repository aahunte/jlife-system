from app import create_app
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    logger.info("应用初始化成功")
except Exception as e:
    logger.error(f"应用初始化失败: {str(e)}")
    raise

if __name__ == '__main__':
    try:
        logger.info("启动服务器...")
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        raise 