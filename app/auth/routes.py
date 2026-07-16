from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'Username already exists'}), 400
        
    import re
    if len(password) < 8:
        return jsonify({'msg': 'Password must be at least 8 characters long'}), 400
    if not re.search(r"[a-z]", password):
        return jsonify({'msg': 'Password must contain at least one lowercase letter'}), 400
    if not re.search(r"[A-Z]", password):
        return jsonify({'msg': 'Password must contain at least one uppercase letter'}), 400
    if not re.search(r"[0-9]", password):
        return jsonify({'msg': 'Password must contain at least one number'}), 400
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'msg': 'Password must contain at least one special character'}), 400
        
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'msg': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token, 'username': user.username}), 200
        
    return jsonify({'msg': 'Invalid credentials'}), 401
