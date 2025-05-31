def validate_user_data(data):
    errors = []
    
    if not data.get('username'):
        errors.append('Username is required')
    elif len(data['username']) < 4:
        errors.append('Username must be at least 4 characters')
    
    if not data.get('email'):
        errors.append('Email is required')
    elif '@' not in data['email']:
        errors.append('Invalid email format')
    
    if not data.get('password'):
        errors.append('Password is required')
    elif len(data['password']) < 6:
        errors.append('Password must be at least 6 characters')
    
    return errors