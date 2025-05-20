from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    中文姓名 = db.Column(db.String(50), nullable=False)
    英文姓名 = db.Column(db.String(100))
    出生日期 = db.Column(db.Date)
    性別 = db.Column(db.String(10))
    身份證號 = db.Column(db.String(20), unique=True)
    電話 = db.Column(db.String(20))
    電郵 = db.Column(db.String(100))
    地址 = db.Column(db.String(200))
    地區 = db.Column(db.String(50))
    經濟狀況 = db.Column(db.String(50))
    職業 = db.Column(db.String(100))
    教育程度 = db.Column(db.String(50))
    婚姻狀況 = db.Column(db.String(20))
    家庭人數 = db.Column(db.Integer)
    緊急聯絡人 = db.Column(db.String(50))
    緊急聯絡電話 = db.Column(db.String(20))
    會員編號 = db.Column(db.String(20), unique=True)
    入會日期 = db.Column(db.Date)
    會員狀態 = db.Column(db.String(20))
    備註 = db.Column(db.Text)
    創建時間 = db.Column(db.DateTime, default=datetime.utcnow)
    更新時間 = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def 年齡(self):
        if not self.出生日期:
            return None
        today = datetime.now().date()
        age = today.year - self.出生日期.year
        if today.month < self.出生日期.month or (today.month == self.出生日期.month and today.day < self.出生日期.day):
            age -= 1
        return age

    def to_dict(self):
        return {
            'id': self.id,
            '中文姓名': self.中文姓名,
            '英文姓名': self.英文姓名,
            '年齡': self.年齡,
            '性別': self.性別,
            '出生日期': self.出生日期.isoformat() if self.出生日期 else None,
            '身份證號': self.身份證號,
            '電話': self.電話,
            '電郵': self.電郵,
            '地址': self.地址,
            '地區': self.地區,
            '經濟狀況': self.經濟狀況,
            '職業': self.職業,
            '教育程度': self.教育程度,
            '婚姻狀況': self.婚姻狀況,
            '家庭人數': self.家庭人數,
            '緊急聯絡人': self.緊急聯絡人,
            '緊急聯絡電話': self.緊急聯絡電話,
            '會員編號': self.會員編號,
            '入會日期': self.入會日期.isoformat() if self.入會日期 else None,
            '會員狀態': self.會員狀態,
            '備註': self.備註,
            '創建時間': self.創建時間.isoformat(),
            '更新時間': self.更新時間.isoformat()
        } 