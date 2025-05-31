from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction
from datetime import datetime, timedelta
from .utils import (
    validate_transaction,
    check_fraud,
    convert_currency
)

wallet_bp = Blueprint('wallet', __name__)

#BALANCE ROUTE
@wallet_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    return jsonify({
        'INR': user.inr_balance,
        'USD': user.usd_balance,
        'YEN': user.yen_balance,
        'EURO': user.euro_balance
    }), 200

#DEPOSIT ROUTE
@wallet_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    errors = validate_transaction(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    amount = float(data['amount'])
    currency = data['currency'].upper()
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
   
    user.update_balance(currency, amount)
    
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        currency=currency,
        transaction_type='deposit'
    )
    
    # FRAUD DETECTION
    fraud_check = check_fraud(user, amount, currency, 'deposit')
    if fraud_check:
        transaction.is_flagged = True
        transaction.flag_reason = fraud_check
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Deposit successful',
        'new_balance': user.get_balance(currency)
    }), 200

#WITHDRAW ROUTE
@wallet_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    errors = validate_transaction(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    amount = float(data['amount'])
    currency = data['currency'].upper()
    balance = user.get_balance(currency)
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    if balance < amount:
        return jsonify({'error': 'Insufficient funds'}), 400
    
    user.update_balance(currency, -amount)
    
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        currency=currency,
        transaction_type='withdrawal'
    )
    
    # FRAUD DETECTION
    fraud_check = check_fraud(user, amount, currency, 'withdrawal')
    if fraud_check:
        transaction.is_flagged = True
        transaction.flag_reason = fraud_check
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Withdrawal successful',
        'new_balance': user.get_balance(currency)
    }), 200

#TRANSFER ROUTE
@wallet_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    data = request.get_json()
    user_id = get_jwt_identity()
    sender = User.query.get(user_id)
    
    errors = validate_transaction(data, require_recipient=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    amount = float(data['amount'])
    currency = data['currency'].upper()
    recipient_id = data['recipient_id']
    recipient_currency = data.get('recipient_currency', currency)
    
    if recipient_id == user_id:
        return jsonify({'error': 'Cannot transfer to yourself'}), 400
    
    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({'error': 'Recipient not found'}), 404
    
    sender_balance = sender.get_balance(currency)
    if sender_balance < amount:
        return jsonify({'error': 'Insufficient funds'}), 400
    
    # Convert currency if needed
    if currency != recipient_currency:
        converted_amount = convert_currency(amount, currency, recipient_currency)
    else:
        converted_amount = amount
    
    # Perform transfer 
    try:
        # Deduct from sender
        sender.update_balance(currency, -amount)
        
        # Add to recipient
        recipient.update_balance(recipient_currency, converted_amount)
        
        # Record sender transaction
        sender_transaction = Transaction(
            user_id=user_id,
            amount=amount,
            currency=currency,
            transaction_type='transfer',
            recipient_id=recipient_id
        )
        
        # Record recipient transaction
        recipient_transaction = Transaction(
            user_id=recipient_id,
            amount=converted_amount,
            currency=recipient_currency,
            transaction_type='transfer',
            recipient_id=user_id
        )
        
        # FRAUD DETECTION
        fraud_check = check_fraud(sender, amount, currency, 'transfer')
        if fraud_check:
            sender_transaction.is_flagged = True
            sender_transaction.flag_reason = fraud_check
            recipient_transaction.is_flagged = True
            recipient_transaction.flag_reason = fraud_check
        
        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transfer successful',
            'new_balance': sender.get_balance(currency),
            'converted_amount': converted_amount,
            'recipient_currency': recipient_currency
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Transfer failed'}), 500


#TRANSACTION route for storing transaction history
@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'currency': t.currency,
        'type': t.transaction_type,
        'recipient_id': t.recipient_id,
        'timestamp': t.timestamp.isoformat(),
        'is_flagged': t.is_flagged,
        'flag_reason': t.flag_reason
    } for t in transactions]), 200