from extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime
#User,Transactions db models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Wallet balances -(INR,USD,YEN,EURO)
    inr_balance = db.Column(db.Float, default=0.0) 
    usd_balance = db.Column(db.Float, default=0.0)
    yen_balance = db.Column(db.Float, default=0.0)
    euro_balance = db.Column(db.Float, default=0.0)
    
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_token(self):
        return create_access_token(identity=self.id)
    
    def get_balance(self, currency):
        if currency == 'INR':
            return self.inr_balance
        elif currency == 'USD':
            return self.usd_balance
        elif currency == 'YEN':
            return self.yen_balance
        elif currency == 'EURO':
            return self.euro_balance
        return 0.0
    
    def update_balance(self, currency, amount):
        if currency == 'INR':
            self.inr_balance += amount
        elif currency == 'USD':
            self.usd_balance += amount
        elif currency == 'YEN':
            self.yen_balance += amount
        elif currency == 'EURO':
            self.euro_balance += amount

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # deposit, withdrawal, transfer
    recipient_id = db.Column(db.Integer, nullable=True) 
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(200), nullable=True)