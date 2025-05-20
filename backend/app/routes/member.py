from flask import Blueprint, request, jsonify, send_file
from ..models.member import Member, db
from ..utils.excel_importer import ExcelImporter
from datetime import datetime
import pandas as pd
import os
from sqlalchemy import or_

member_bp = Blueprint('member', __name__)

def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    wrapper.__name__ = func.__name__
    return wrapper

def get_excel_path():
    """获取Excel文件路径"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    excel_path = os.path.join(root_dir, 'update.xlsx')
    print(f"Excel文件路径: {excel_path}")
    # 确保目录存在
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    return excel_path

def get_all_members_data():
    """获取所有会员数据并转换为适合Excel的格式"""
    try:
        print("開始獲取會員數據...")
        members = Member.query.all()
        print(f"從數據庫獲取到 {len(members)} 條會員記錄")
        
        data = []
        for member in members:
            try:
                member_dict = member.to_dict()
                # 转换日期为字符串格式
                if member_dict.get('出生日期'):
                    member_dict['出生日期'] = datetime.strptime(member_dict['出生日期'], '%Y-%m-%d').strftime('%Y-%m-%d')
                if member_dict.get('入會日期'):
                    member_dict['入會日期'] = datetime.strptime(member_dict['入會日期'], '%Y-%m-%d').strftime('%Y-%m-%d')
                data.append(member_dict)
            except Exception as e:
                print(f"處理會員數據時出錯 (ID: {member.id}): {str(e)}")
                continue
        
        print(f"成功處理 {len(data)} 條會員數據")
        return data
    except Exception as e:
        print(f"獲取會員數據失敗: {str(e)}")
        return []

def update_excel_file(member_data):
    """更新Excel文件，添加新会员数据"""
    try:
        excel_path = get_excel_path()
        print(f"正在更新Excel文件: {excel_path}")
        
        # 获取所有会员数据
        all_data = get_all_members_data()
        print(f"获取到 {len(all_data)} 条会员数据")
        
        # 创建DataFrame并设置列顺序
        columns = [
            '會員編號', '中文姓名', '英文姓名', '性別', '出生日期', '年齡',
            '身份證號', '電話', '電郵', '地址', '地區', '經濟狀況',
            '職業', '教育程度', '婚姻狀況', '家庭人數', '緊急聯絡人',
            '緊急聯絡電話', '入會日期', '會員狀態', '備註'
        ]
        df = pd.DataFrame(all_data)
        df = df[columns]  # 重新排序列
        
        # 如果文件存在，读取现有数据
        if os.path.exists(excel_path):
            existing_df = pd.read_excel(excel_path)
            print(f"讀取到現有Excel文件，包含 {len(existing_df)} 行數據")
            
            # 合并数据，避免重复
            df = pd.concat([existing_df, df], ignore_index=True)
            df = df.drop_duplicates(subset=['會員編號'], keep='last')
            print(f"合併後共有 {len(df)} 行數據")
        
        # 保存到Excel文件
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"Excel文件已成功更新到: {excel_path}")
        return True, f"Excel文件已更新到: {excel_path}"
    except Exception as e:
        print(f"更新Excel文件失败: {str(e)}")
        return False, f"更新Excel文件失败: {str(e)}"

@member_bp.route('/', methods=['GET'])
def get_members():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    members = Member.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'total': members.total,
        'pages': members.pages,
        'current_page': members.page,
        'members': [member.to_dict() for member in members.items]
    })

@member_bp.route('/<string:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.filter_by(會員編號=member_id).first_or_404()
    return jsonify(member.to_dict())

@member_bp.route('/', methods=['POST'])
@handle_error
def create_member():
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['中文姓名', '性別', '身份證號', '經濟狀況', '地址', '婚姻狀況']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必填字段：{field}'}), 400
    
    # 检查身份证号是否已存在
    if Member.query.filter_by(身份證號=data['身份證號']).first():
        return jsonify({'error': '該身份證號已註冊'}), 409
    
    # 检查会员编号是否已存在
    if Member.query.filter_by(會員編號=data['會員編號']).first():
        return jsonify({'error': '該會員編號已存在'}), 409
    
    # 转换日期字符串为日期对象
    if data.get('出生日期'):
        data['出生日期'] = datetime.strptime(data['出生日期'], '%Y-%m-%d').date()
    if data.get('入會日期'):
        data['入會日期'] = datetime.strptime(data['入會日期'], '%Y-%m-%d').date()
    
    # 创建会员记录
    member = Member(**data)
    db.session.add(member)
    db.session.commit()
    
    # 更新Excel文件
    success, message = update_excel_file(member.to_dict())
    if not success:
        print(f"Warning: {message}")
    
    return jsonify(member.to_dict()), 201

@member_bp.route('/<string:member_id>', methods=['PUT'])
@handle_error
def update_member(member_id):
    member = Member.query.filter_by(會員編號=member_id).first_or_404()
    data = request.get_json()
    
    # 转换日期字符串为日期对象
    if data.get('出生日期'):
        data['出生日期'] = datetime.strptime(data['出生日期'], '%Y-%m-%d').date()
    if data.get('入會日期'):
        data['入會日期'] = datetime.strptime(data['入會日期'], '%Y-%m-%d').date()
    
    for key, value in data.items():
        setattr(member, key, value)
    
    db.session.commit()
    return jsonify(member.to_dict())

@member_bp.route('/<string:member_id>', methods=['DELETE'])
@handle_error
def delete_member(member_id):
    member = Member.query.filter_by(會員編號=member_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    return '', 204

@member_bp.route('/import', methods=['POST'])
@handle_error
def import_members():
    if 'file' not in request.files:
        return jsonify({'error': '沒有文件上傳'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': '請上傳Excel文件'}), 400
    
    success, message = ExcelImporter.import_members(file)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400

@member_bp.route('/stats', methods=['GET'])
@handle_error
def get_stats():
    total_members = Member.query.count()
    age_stats = db.session.query(
        db.func.count(Member.id).label('count'),
        Member.年齡
    ).group_by(Member.年齡).all()
    
    area_stats = db.session.query(
        db.func.count(Member.id).label('count'),
        Member.地區
    ).group_by(Member.地區).all()
    
    economic_stats = db.session.query(
        db.func.count(Member.id).label('count'),
        Member.經濟狀況
    ).group_by(Member.經濟狀況).all()
    
    return jsonify({
        'total_members': total_members,
        'age_distribution': [{'age': age, 'count': count} for count, age in age_stats],
        'area_distribution': [{'area': area, 'count': count} for count, area in area_stats],
        'economic_distribution': [{'status': status, 'count': count} for count, status in economic_stats]
    })

@member_bp.route('/export', methods=['GET'])
@handle_error
def export_members():
    # 获取所有会员数据
    members = Member.query.all()
    
    # 创建DataFrame
    data = []
    for member in members:
        member_dict = member.to_dict()
        # 将日期转换为字符串格式
        if member_dict['出生日期']:
            member_dict['出生日期'] = datetime.strptime(member_dict['出生日期'], '%Y-%m-%d').strftime('%Y-%m-%d')
        if member_dict['入會日期']:
            member_dict['入會日期'] = datetime.strptime(member_dict['入會日期'], '%Y-%m-%d').strftime('%Y-%m-%d')
        data.append(member_dict)
    
    df = pd.DataFrame(data)
    
    # 确保导出目录存在
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    # 生成文件名（使用当前时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'members_export_{timestamp}.xlsx'
    filepath = os.path.join(export_dir, filename)
    
    # 导出到Excel
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    # 发送文件
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@member_bp.route('/search', methods=['GET'])
@handle_error
def search_members():
    term = request.args.get('term', '')
    print(f"搜索關鍵詞: {term}")
    
    if not term:
        print("警告：搜索關鍵詞為空")
        return jsonify([])
    
    # 在多个字段中搜索
    search_query = or_(
        Member.中文姓名.ilike(f'%{term}%'),
        Member.英文姓名.ilike(f'%{term}%'),
        Member.身份證號.ilike(f'%{term}%'),
        Member.會員編號.ilike(f'%{term}%'),
        Member.電話.ilike(f'%{term}%'),
        Member.地址.ilike(f'%{term}%')
    )
    
    members = Member.query.filter(search_query).all()
    print(f"找到 {len(members)} 條記錄")
    
    result = [member.to_dict() for member in members]
    print(f"返回數據: {result}")
    
    return jsonify(result)

@member_bp.route('/update-excel', methods=['POST'])
@handle_error
def update_excel():
    """手动更新Excel文件"""
    try:
        print("開始更新Excel文件...")
        
        # 获取所有会员数据
        all_data = get_all_members_data()
        print(f"獲取到 {len(all_data)} 條會員數據")
        
        if not all_data:
            print("警告：沒有找到任何會員數據")
            return jsonify({'error': '沒有找到任何會員數據'}), 404
        
        # 创建DataFrame并设置列顺序
        columns = [
            '會員編號', '中文姓名', '英文姓名', '性別', '出生日期', '年齡',
            '身份證號', '電話', '電郵', '地址', '地區', '經濟狀況',
            '職業', '教育程度', '婚姻狀況', '家庭人數', '緊急聯絡人',
            '緊急聯絡電話', '入會日期', '會員狀態', '備註'
        ]
        
        # 列名映射
        column_mapping = {
            '會籍': '會員編號',
            '中文姓名': '中文姓名',
            '英文姓名': '英文姓名',
            '性別': '性別',
            '年齡': '年齡',
            '手提電話': '電話',
            '地址': '地址',
            '經濟狀況': '經濟狀況',
            '婚姻狀況': '婚姻狀況',
            '入會日期': '入會日期'
        }
        
        try:
            df = pd.DataFrame(all_data)
            print(f"成功創建DataFrame，包含 {len(df)} 行數據")
            print(f"DataFrame列: {df.columns.tolist()}")
            
            # 确保所有必需的列都存在
            for col in columns:
                if col not in df.columns:
                    print(f"警告：列 {col} 不存在，添加空列")
                    df[col] = None
            
            # 重新排序列
            df = df[columns]
            print(f"重新排序列後的DataFrame列: {df.columns.tolist()}")
        except Exception as e:
            print(f"創建DataFrame失敗: {str(e)}")
            print(f"數據內容: {all_data}")
            return jsonify({'error': f'創建數據表失敗: {str(e)}'}), 500
        
        # 获取Excel文件路径
        excel_path = '/home/karos/JLife/update.xlsx'
        print(f"正在更新Excel文件: {excel_path}")
        
        try:
            # 如果文件存在，读取现有数据
            if os.path.exists(excel_path):
                try:
                    existing_df = pd.read_excel(excel_path)
                    print(f"讀取到現有Excel文件，包含 {len(existing_df)} 行數據")
                    print(f"現有Excel文件列: {existing_df.columns.tolist()}")
                    
                    # 如果现有文件没有正确的列名，尝试使用第一行作为列名
                    if '會員編號' not in existing_df.columns:
                        print("現有Excel文件列名不正確，嘗試使用第一行作為列名")
                        existing_df.columns = existing_df.iloc[0]
                        existing_df = existing_df.iloc[1:]
                        existing_df = existing_df.reset_index(drop=True)
                        print(f"調整後的列名: {existing_df.columns.tolist()}")
                    
                    # 重命名列
                    for old_col, new_col in column_mapping.items():
                        if old_col in existing_df.columns:
                            existing_df = existing_df.rename(columns={old_col: new_col})
                            print(f"重命名列: {old_col} -> {new_col}")
                    
                    # 确保现有数据的列名一致
                    for col in columns:
                        if col not in existing_df.columns:
                            print(f"警告：現有Excel文件缺少列 {col}，添加空列")
                            existing_df[col] = None
                    existing_df = existing_df[columns]
                    
                    # 合并数据，避免重复
                    df = pd.concat([existing_df, df], ignore_index=True)
                    df = df.drop_duplicates(subset=['會員編號'], keep='last')
                    print(f"合併後共有 {len(df)} 行數據")
                except Exception as e:
                    print(f"讀取現有Excel文件失敗: {str(e)}")
                    print("將創建新的Excel文件")
            
            # 保存到Excel文件
            try:
                df.to_excel(excel_path, index=False, engine='openpyxl')
                print(f"Excel文件已成功更新到: {excel_path}")
            except Exception as e:
                print(f"保存Excel文件失敗: {str(e)}")
                return jsonify({'error': f'保存Excel文件失敗: {str(e)}'}), 500
            
            # 验证文件是否成功创建
            if os.path.exists(excel_path):
                file_size = os.path.getsize(excel_path)
                print(f"文件已成功創建，大小: {file_size} 字節")
            else:
                print(f"警告：文件似乎沒有被創建: {excel_path}")
                return jsonify({'error': '文件創建失敗'}), 500
                
        except Exception as e:
            print(f"更新Excel文件失敗: {str(e)}")
            return jsonify({'error': f'更新Excel文件失敗: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Excel文件已更新，共更新 {len(df)} 條記錄',
            'path': excel_path
        })
    except Exception as e:
        print(f"更新Excel文件失敗: {str(e)}")
        import traceback
        print(f"錯誤堆棧: {traceback.format_exc()}")
        return jsonify({'error': f'更新Excel文件失敗: {str(e)}'}), 500 