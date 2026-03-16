from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class AuditRecord(Base):
    __tablename__ = 'audit_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    factory_name = Column(String(100), nullable=False)
    evaluator_email = Column(String(100), nullable=False)
    audit_date = Column(DateTime, default=datetime.now)
    
    # 对应你 8 个模块的分数
    score_pattern = Column(Float, default=0.0)
    score_fabric = Column(Float, default=0.0)
    score_pre_prod = Column(Float, default=0.0)
    score_cutting = Column(Float, default=0.0)
    score_sewing = Column(Float, default=0.0)
    score_finishing = Column(Float, default=0.0)
    score_qc = Column(Float, default=0.0)
    score_others = Column(Float, default=0.0)
    
    total_score = Column(Float)
    # 存储完整的 JSON 原始数据备份（可选，方便以后扩展）
    raw_data = Column(Text) 

# 创建数据库引擎（文件会保存在 data/factory.db）
engine = create_engine('sqlite:///data/factory.db', check_same_thread=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
def save_audit(data_dict):
    """将一条评估记录保存到数据库"""
    db = SessionLocal()
    new_record = AuditRecord(
        factory_name=data_dict['factory'],
        evaluator_email=data_dict['user'],
        total_score=data_dict['total_score'],
        score_pattern=data_dict['scores'].get('纸样制作', 0),
        # ... 依次添加其他分数字段
        raw_data=str(data_dict) # 将整个字典转成字符串存入备用
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    db.close()
    return new_record

def get_all_audits():
    """读取所有记录，返回 DataFrame 方便 Streamlit 显示"""
    import pandas as pd
    return pd.read_sql("SELECT * FROM audit_records", engine)
