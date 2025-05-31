from datetime import datetime, timedelta
from models import db, Transaction
from config import Config

def validate_transaction(data, require_recipient=False):
    errors = []
    
    if not data.get('amount'):
        errors.append('Amount is required')
    else:
        try:
            float(data['amount'])
        except ValueError:
            errors.append('Amount must be a number')
    
    if not data.get('currency'):
        errors.append('Currency is required')
    elif data['currency'].upper() not in Config.SUPPORTED_CURRENCIES:
        errors.append(f"Unsupported currency. Supported: {', '.join(Config.SUPPORTED_CURRENCIES)}")
    
    if require_recipient and not data.get('recipient_id'):
        errors.append('Recipient ID is required for transfers')
    
    return errors

def check_fraud(user, amount, currency, transaction_type):
    # Check for large withdrawals
    if transaction_type == 'withdrawal' and amount > 10000: 
        return "Large withdrawal amount"
    
    # Check for sudden large deposits
    if transaction_type == 'deposit' and amount > 50000:  
        return "Large deposit amount"
    
    # Check for multiple transfers in short time
    recent_transfers = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'transfer',
        Transaction.timestamp >= datetime.now() - timedelta(minutes=5)
    ).count()
    
    if recent_transfers >= 5:  # more than 5 transfers in 5 minutes
        return "High frequency of transfers"
    
    return None

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    
    rate = Config.CURRENCY_CONVERSION_RATES[from_currency][to_currency]
    return amount * rate