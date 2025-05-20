from datetime import datetime
from .member import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    活動編號 = db.Column(db.String(50), unique=True, nullable=False)
    活動名稱 = db.Column(db.String(200), nullable=False)
    活動日期 = db.Column(db.Date, nullable=False)
    活動時間 = db.Column(db.Time)
    活動地點 = db.Column(db.String(200))
    活動類型 = db.Column(db.String(50))
    主辦單位 = db.Column(db.String(100))
    負責人 = db.Column(db.String(50))
    預計人數 = db.Column(db.Integer)
    備註 = db.Column(db.Text)
    創建時間 = db.Column(db.DateTime, default=datetime.utcnow)
    更新時間 = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            '活動編號': self.活動編號,
            '活動名稱': self.活動名稱,
            '活動日期': self.活動日期.isoformat(),
            '活動時間': self.活動時間.isoformat() if self.活動時間 else None,
            '活動地點': self.活動地點,
            '活動類型': self.活動類型,
            '主辦單位': self.主辦單位,
            '負責人': self.負責人,
            '預計人數': self.預計人數,
            '備註': self.備註,
            '創建時間': self.創建時間.isoformat(),
            '更新時間': self.更新時間.isoformat()
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    會員編號 = db.Column(db.String(20), db.ForeignKey('members.會員編號'), nullable=False)
    活動編號 = db.Column(db.String(50), db.ForeignKey('events.活動編號'), nullable=False)
    是否出席 = db.Column(db.Boolean, default=False)
    簽到時間 = db.Column(db.DateTime)
    簽退時間 = db.Column(db.DateTime)
    備註 = db.Column(db.Text)
    創建時間 = db.Column(db.DateTime, default=datetime.utcnow)
    更新時間 = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            '會員編號': self.會員編號,
            '活動編號': self.活動編號,
            '是否出席': self.是否出席,
            '簽到時間': self.簽到時間.isoformat() if self.簽到時間 else None,
            '簽退時間': self.簽退時間.isoformat() if self.簽退時間 else None,
            '備註': self.備註,
            '創建時間': self.創建時間.isoformat(),
            '更新時間': self.更新時間.isoformat()
        } 