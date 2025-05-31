from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/flagged-transactions', methods=['GET'])
@jwt_required()
def get_flagged_transactions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    transactions = Transaction.query.filter_by(is_flagged=True).order_by(Transaction.timestamp.desc()).all()
    
    return jsonify([{
        'id': t.id,
        'user_id': t.user_id,
        'amount': t.amount,
        'currency': t.currency,
        'type': t.transaction_type,
        'recipient_id': t.recipient_id,
        'timestamp': t.timestamp.isoformat(),
        'flag_reason': t.flag_reason
    } for t in transactions]), 200

@admin_bp.route('/total-balances', methods=['GET'])
@jwt_required()
def get_total_balances():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    
    total_inr = sum(u.inr_balance for u in users)
    total_usd = sum(u.usd_balance for u in users)
    total_yen = sum(u.yen_balance for u in users)
    total_euro = sum(u.euro_balance for u in users)
    
    return jsonify({
        'total_INR': total_inr,
        'total_USD': total_usd,
        'total_YEN': total_yen,
        'total_EURO': total_euro
    }), 200

@admin_bp.route('/top-users', methods=['GET'])
@jwt_required()
def get_top_users():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Top by balance
    top_balance = User.query.order_by(User.inr_balance + User.usd_balance + User.yen_balance + User.euro_balance).limit(10).all()
    
    # Top by transaction count 
    users = User.query.all()
    top_transaction_users = sorted(
        users,
        key=lambda u: len(u.transactions),
        reverse=True
    )[:10]
    
    return jsonify({
        'by_balance': [{
            'id': u.id,
            'username': u.username,
            'total_balance': u.inr_balance + u.usd_balance + u.yen_balance + u.euro_balance
        } for u in top_balance],
        'by_transactions': [{
            'id': u.id,
            'username': u.username,
            'transaction_count': len(u.transactions)
        } for u in top_transaction_users]
    }), 200