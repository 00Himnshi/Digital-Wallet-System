from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token
from .utils import validate_user_data

auth_bp = Blueprint('auth', __name__)
#register user
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = validate_user_data(data)
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'token': user.get_token()
    }), 201
#login user
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({
        'message': 'Logged in successfully',
        'token': user.get_token()
    }), 200