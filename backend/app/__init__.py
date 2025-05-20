from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .models.member import db
import os
import logging

def create_app(test_config=None):
    app = Flask(__name__)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 基础配置
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///jlife.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev')
    )
    
    # 测试配置
    if test_config:
        app.config.update(test_config)
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    
    # 注册蓝图
    try:
        from .routes import member_bp, inventory_bp, attendance_bp
        app.register_blueprint(member_bp, url_prefix='/api/members')
        app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
        app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    except ImportError as e:
        logging.error(f"蓝图注册失败: {str(e)}")
        raise
    
    # 创建数据库表
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        logging.error(f"数据库初始化失败: {str(e)}")
        raise
    
    return app 