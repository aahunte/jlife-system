import os
import sys
from app import create_app
from app.utils.excel_importer import ExcelImporter

def import_data():
    app = create_app()
    with app.app_context():
        # 获取当前目录下的Excel文件
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            print("当前目录下没有找到Excel文件")
            return
        
        print("找到以下Excel文件：")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        # 让用户选择要导入的文件
        while True:
            try:
                choice = int(input("\n请选择要导入的文件编号（输入0退出）："))
                if choice == 0:
                    return
                if 1 <= choice <= len(excel_files):
                    break
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")
        
        selected_file = excel_files[choice - 1]
        print(f"\n正在导入文件：{selected_file}")
        
        # 根据文件名判断导入类型
        if 'member' in selected_file.lower():
            success, message = ExcelImporter.import_members(selected_file)
        elif 'inventory' in selected_file.lower():
            success, message = ExcelImporter.import_inventory(selected_file)
        elif 'event' in selected_file.lower():
            success, message = ExcelImporter.import_events(selected_file)
        elif 'attendance' in selected_file.lower():
            success, message = ExcelImporter.import_attendance(selected_file)
        else:
            print("无法确定文件类型，请确保文件名包含：member、inventory、event或attendance")
            return
        
        print(message)
        if success:
            print("数据导入成功！")
        else:
            print("数据导入失败！")

if __name__ == '__main__':
    import_data() 