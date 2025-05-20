from flask import Blueprint, request, jsonify
from ..models.inventory import Inventory
from ..models.member import db
from ..utils.excel_importer import ExcelImporter
from datetime import datetime
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    inventory = Inventory.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'total': inventory.total,
        'pages': inventory.pages,
        'current_page': inventory.page,
        'items': [item.to_dict() for item in inventory.items]
    })

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@inventory_bp.route('/', methods=['POST'])
def create_item():
    data = request.get_json()
    item = Inventory(**data)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(item, key, value)
    db.session.commit()
    return jsonify(item.to_dict())

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204

@inventory_bp.route('/import', methods=['POST'])
def import_inventory():
    if 'file' not in request.files:
        return jsonify({'error': '沒有文件上傳'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': '請上傳Excel文件'}), 400
    
    success, message = ExcelImporter.import_inventory(file)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400

@inventory_bp.route('/stats/yearly', methods=['GET'])
def get_yearly_stats():
    year = request.args.get('year', datetime.now().year, type=int)
    
    # 按月份统计总重量
    monthly_weight = db.session.query(
        func.sum(Inventory.總重量_kg).label('total_weight'),
        func.strftime('%m', Inventory.月份).label('month')
    ).filter(
        func.strftime('%Y', Inventory.月份) == str(year)
    ).group_by('month').all()
    
    # 按产品统计总重量和数量
    product_stats = db.session.query(
        Inventory.產品描述,
        func.sum(Inventory.總重量_kg).label('total_weight'),
        func.sum(Inventory.數量).label('total_count')
    ).filter(
        func.strftime('%Y', Inventory.月份) == str(year)
    ).group_by(Inventory.產品描述).all()
    
    # 按物资来源统计总金额
    source_stats = db.session.query(
        Inventory.物資來源,
        func.sum(Inventory.總金額).label('total_amount')
    ).filter(
        func.strftime('%Y', Inventory.月份) == str(year)
    ).group_by(Inventory.物資來源).all()
    
    return jsonify({
        'year': year,
        'monthly_weight': [{'month': month, 'total_weight': weight} for weight, month in monthly_weight],
        'product_stats': [{
            'product': product,
            'total_weight': weight,
            'total_count': count
        } for product, weight, count in product_stats],
        'source_stats': [{
            'source': source,
            'total_amount': amount
        } for source, amount in source_stats]
    }) 