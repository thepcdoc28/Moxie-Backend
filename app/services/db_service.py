from app import db
from app.models import Message

def save_message(session_id, role, content, metadata=None):
    msg = Message(session_id=session_id, role=role, content=content, metadata_=metadata)
    db.session.add(msg)
    db.session.commit()
    return msg

def get_messages(session_id):
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages]
