import json
from database import SessionLocal, AuditRecord

def run_migration():
    with open('data/evaluations.json', 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    db = SessionLocal()
    for item in old_data:
        # 这里的字段名要根据你旧 JSON 的实际格式对齐
        record = AuditRecord(
            factory_name=item.get('factory'),
            evaluator_email=item.get('user'),
            total_score=item.get('total_score'),
            # ... 映射分数
        )
        db.add(record)
    db.commit()
    db.close()
    print("旧数据迁移完成！")

if __name__ == "__main__":
    run_migration()
