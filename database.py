# database.py
import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量（避免硬编码数据库路径）
load_dotenv()

# 配置数据库（SQLite 无需额外安装，文件持久化存储）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./factory_audit.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite 专用参数
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定义评估记录表（对应原来的 evaluations.json）
class AuditRecord(Base):
    __tablename__ = "audit_records"
    
    id = Column(String, primary_key=True)  # 评估记录ID
    factory_name = Column(String, nullable=False)  # 工厂名称
    auditor = Column(String, nullable=False)  # 审核员
    audit_date = Column(DateTime, default=datetime.now)  # 审核日期
    items = Column(Text)  # 评估项（JSON 字符串存储）
    score = Column(Integer)  # 总分
    media_files = Column(Text)  # 关联的图片路径（逗号分隔）
    pdf_path = Column(String)  # PDF 生成路径

# 创建数据库表（首次运行执行）
Base.metadata.create_all(bind=engine)

# 数据库会话依赖（每次操作数据库时调用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
