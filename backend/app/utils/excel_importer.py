import pandas as pd
from datetime import datetime
from ..models.member import Member, db
from ..models.inventory import Inventory
from ..models.attendance import Event, Attendance

class ExcelImporter:
    @staticmethod
    def import_members(file_path):
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                member = Member(
                    中文姓名=row.get('中文姓名'),
                    英文姓名=row.get('英文姓名'),
                    年齡=row.get('年齡'),
                    性別=row.get('性別'),
                    出生日期=pd.to_datetime(row.get('出生日期')).date() if pd.notna(row.get('出生日期')) else None,
                    身份證號=row.get('身份證號'),
                    電話=row.get('電話'),
                    電郵=row.get('電郵'),
                    地址=row.get('地址'),
                    地區=row.get('地區'),
                    經濟狀況=row.get('經濟狀況'),
                    職業=row.get('職業'),
                    教育程度=row.get('教育程度'),
                    婚姻狀況=row.get('婚姻狀況'),
                    家庭人數=row.get('家庭人數'),
                    緊急聯絡人=row.get('緊急聯絡人'),
                    緊急聯絡電話=row.get('緊急聯絡電話'),
                    會員編號=row.get('會員編號'),
                    入會日期=pd.to_datetime(row.get('入會日期')).date() if pd.notna(row.get('入會日期')) else None,
                    會員狀態=row.get('會員狀態'),
                    備註=row.get('備註')
                )
                db.session.add(member)
            db.session.commit()
            return True, "会员数据导入成功"
        except Exception as e:
            db.session.rollback()
            return False, f"会员数据导入失败: {str(e)}"

    @staticmethod
    def import_inventory(file_path):
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                inventory = Inventory(
                    月份=pd.to_datetime(row.get('月份')).date() if pd.notna(row.get('月份')) else None,
                    產品編號=row.get('產品編號'),
                    產品描述=row.get('產品描述'),
                    數量=row.get('數量'),
                    單位=row.get('單位'),
                    總重量_kg=row.get('總重量_kg'),
                    單價=row.get('單價'),
                    總金額=row.get('總金額'),
                    物資來源=row.get('物資來源'),
                    供應商=row.get('供應商'),
                    存放位置=row.get('存放位置'),
                    備註=row.get('備註')
                )
                db.session.add(inventory)
            db.session.commit()
            return True, "库存数据导入成功"
        except Exception as e:
            db.session.rollback()
            return False, f"库存数据导入失败: {str(e)}"

    @staticmethod
    def import_events(file_path):
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                event = Event(
                    活動編號=row.get('活動編號'),
                    活動名稱=row.get('活動名稱'),
                    活動日期=pd.to_datetime(row.get('活動日期')).date() if pd.notna(row.get('活動日期')) else None,
                    活動時間=pd.to_datetime(row.get('活動時間')).time() if pd.notna(row.get('活動時間')) else None,
                    活動地點=row.get('活動地點'),
                    活動類型=row.get('活動類型'),
                    主辦單位=row.get('主辦單位'),
                    負責人=row.get('負責人'),
                    預計人數=row.get('預計人數'),
                    備註=row.get('備註')
                )
                db.session.add(event)
            db.session.commit()
            return True, "活动数据导入成功"
        except Exception as e:
            db.session.rollback()
            return False, f"活动数据导入失败: {str(e)}"

    @staticmethod
    def import_attendance(file_path):
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                attendance = Attendance(
                    會員編號=row.get('會員編號'),
                    活動編號=row.get('活動編號'),
                    是否出席=row.get('是否出席', False),
                    簽到時間=pd.to_datetime(row.get('簽到時間')) if pd.notna(row.get('簽到時間')) else None,
                    簽退時間=pd.to_datetime(row.get('簽退時間')) if pd.notna(row.get('簽退時間')) else None,
                    備註=row.get('備註')
                )
                db.session.add(attendance)
            db.session.commit()
            return True, "考勤数据导入成功"
        except Exception as e:
            db.session.rollback()
            return False, f"考勤数据导入失败: {str(e)}" 