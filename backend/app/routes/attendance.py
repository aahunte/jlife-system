from flask import Blueprint, request, jsonify
from ..models.attendance import Event, Attendance
from ..models.member import db
from ..utils.excel_importer import ExcelImporter
from datetime import datetime
from sqlalchemy import func

attendance_bp = Blueprint('attendance', __name__)

# 活动相关路由
@attendance_bp.route('/events', methods=['GET'])
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    events = Event.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'total': events.total,
        'pages': events.pages,
        'current_page': events.page,
        'events': [event.to_dict() for event in events.items]
    })

@attendance_bp.route('/events/<string:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.filter_by(活動編號=event_id).first_or_404()
    return jsonify(event.to_dict())

@attendance_bp.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201

@attendance_bp.route('/events/<string:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.filter_by(活動編號=event_id).first_or_404()
    data = request.get_json()
    for key, value in data.items():
        setattr(event, key, value)
    db.session.commit()
    return jsonify(event.to_dict())

@attendance_bp.route('/events/<string:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.filter_by(活動編號=event_id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return '', 204

# 考勤相关路由
@attendance_bp.route('/', methods=['GET'])
def get_attendance():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    event_id = request.args.get('event_id')
    
    query = Attendance.query
    if event_id:
        query = query.filter_by(活動編號=event_id)
    
    attendance = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'total': attendance.total,
        'pages': attendance.pages,
        'current_page': attendance.page,
        'records': [record.to_dict() for record in attendance.items]
    })

@attendance_bp.route('/mark', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    member_id = data.get('會員編號')
    event_id = data.get('活動編號')
    
    if not member_id or not event_id:
        return jsonify({'error': '缺少必要参数'}), 400
    
    attendance = Attendance.query.filter_by(
        會員編號=member_id,
        活動編號=event_id
    ).first()
    
    if attendance:
        attendance.是否出席 = True
        attendance.簽到時間 = datetime.now()
    else:
        attendance = Attendance(
            會員編號=member_id,
            活動編號=event_id,
            是否出席=True,
            簽到時間=datetime.now()
        )
        db.session.add(attendance)
    
    db.session.commit()
    return jsonify(attendance.to_dict())

@attendance_bp.route('/import', methods=['POST'])
def import_attendance():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': '请上传Excel文件'}), 400
    
    success, message = ExcelImporter.import_attendance(file)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400

@attendance_bp.route('/stats', methods=['GET'])
def get_attendance_stats():
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': '缺少活动编号'}), 400
    
    # 获取活动信息
    event = Event.query.filter_by(活動編號=event_id).first_or_404()
    
    # 统计出席情况
    attendance_stats = db.session.query(
        func.count(Attendance.id).label('total'),
        func.sum(case([(Attendance.是否出席 == True, 1)], else_=0)).label('present')
    ).filter_by(活動編號=event_id).first()
    
    total = attendance_stats.total or 0
    present = attendance_stats.present or 0
    
    return jsonify({
        'event': event.to_dict(),
        'total_registered': total,
        'total_present': present,
        'attendance_rate': (present / total * 100) if total > 0 else 0
    }) 