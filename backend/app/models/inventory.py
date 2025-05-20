from datetime import datetime
from .member import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    月份 = db.Column(db.Date, nullable=False)
    產品編號 = db.Column(db.String(50), nullable=False)
    產品描述 = db.Column(db.String(200))
    數量 = db.Column(db.Integer)
    單位 = db.Column(db.String(20))
    總重量_kg = db.Column(db.Float)
    單價 = db.Column(db.Float)
    總金額 = db.Column(db.Float)
    物資來源 = db.Column(db.String(100))
    供應商 = db.Column(db.String(100))
    存放位置 = db.Column(db.String(100))
    備註 = db.Column(db.Text)
    創建時間 = db.Column(db.DateTime, default=datetime.utcnow)
    更新時間 = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            '月份': self.月份.isoformat(),
            '產品編號': self.產品編號,
            '產品描述': self.產品描述,
            '數量': self.數量,
            '單位': self.單位,
            '總重量_kg': self.總重量_kg,
            '單價': self.單價,
            '總金額': self.總金額,
            '物資來源': self.物資來源,
            '供應商': self.供應商,
            '存放位置': self.存放位置,
            '備註': self.備註,
            '創建時間': self.創建時間.isoformat(),
            '更新時間': self.更新時間.isoformat()
        } 