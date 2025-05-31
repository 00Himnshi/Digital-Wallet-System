import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wallet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key-here'
    SUPPORTED_CURRENCIES = ['INR', 'USD', 'YEN', 'EURO']
    CURRENCY_CONVERSION_RATES = {
        'INR': {'USD': 0.012, 'YEN': 1.77, 'EURO': 0.011},
        'USD': {'INR': 83.37, 'YEN': 147.66, 'EURO': 0.92},
        'YEN': {'INR': 0.56, 'USD': 0.0068, 'EURO': 0.0062},
        'EURO': {'INR': 89.91, 'USD': 1.08, 'YEN': 161.29}
    }