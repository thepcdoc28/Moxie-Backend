from flask import request
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app import socketio
from app.services.db_service import save_message, get_messages
from app.services.agents import get_agent_for_request

active_users = {}

@socketio.on('connect')
def handle_connect(auth):
    token = auth.get('token') if auth else None
    if not token:
        disconnect()
        return False
    
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        active_users[request.sid] = user_id
    except Exception as e:
        print(f"Socket connection rejected: {e}")
        disconnect()
        return False

@socketio.on('disconnect')
def handle_disconnect():
    active_users.pop(request.sid, None)

@socketio.on('send_message')
def handle_message(data):
    session_id = data.get('session_id')
    content = data.get('content')
    model = data.get('model', 'Moxie Core')
    
    if not session_id or not content:
        emit('error', {'msg': 'Missing session_id or content'})
        return
        
    save_message(session_id, 'user', content)
    history = get_messages(session_id)
    
    agent = get_agent_for_request(content, model)
    agent_name = agent.__class__.__name__
    
    emit('ai_chunk_start', {'session_id': session_id, 'agent': agent_name})
    
    full_response = ""
    for chunk in agent.process_message(history):
        full_response += chunk
        emit('ai_chunk', {'session_id': session_id, 'chunk': chunk})
        socketio.sleep(0.005) # Tiny yield to ensure smooth non-blocking websocket flow
        
    save_message(session_id, 'ai', full_response, metadata={"agent": agent_name})
    emit('ai_chunk_end', {'session_id': session_id, 'full_response': full_response, 'agent': agent_name})
