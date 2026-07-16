from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Session, Message

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    user_id = get_jwt_identity()
    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()
    return jsonify([
        {'id': s.id, 'title': s.title, 'created_at': s.created_at.isoformat()} 
        for s in sessions
    ]), 200

@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    title = data.get('title', 'New Chat')
    
    new_session = Session(user_id=user_id, title=title)
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({'id': new_session.id, 'title': new_session.title}), 201

@chat_bp.route('/sessions/<session_id>/messages', methods=['GET'])
@jwt_required()
def get_session_messages(session_id):
    user_id = get_jwt_identity()
    
    # Verify session belongs to user
    session = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({'msg': 'Session not found or unauthorized'}), 404
        
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()
    return jsonify([
        {
            'role': msg.role, 
            'content': msg.content, 
            'agent': msg.metadata_.get('agent') if msg.metadata_ else None
        } 
        for msg in messages
    ]), 200
