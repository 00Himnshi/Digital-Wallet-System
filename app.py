from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from extensions import db
from config import Config
from auth.routes import auth_bp
from wallet.routes import wallet_bp
from admin.routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)