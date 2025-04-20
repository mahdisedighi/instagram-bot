from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=True)
    last_message_id = Column(Text, nullable=True)
    usage = Column(Integer, default=0)
    chat_id = Column(Text, nullable=True)
    lastActive = Column(DateTime, default=datetime.utcnow)
    text_custom = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    session_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')

    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}')>"

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), default=22362518038)
    user_message = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')

class Rols(Base):
    __tablename__ = 'rols'
    id = Column(Integer, primary_key=True)
    rols = Column(String(500), nullable=False)

    def __repr__(self):
        return f"<Rols(rols='{self.rols}')>"

class UserMessageLimit(Base):
    __tablename__ = 'user_message_limits'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    message_count = Column(Integer, default=0)
    last_message_time = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')

class CheckReferral(Base):
    __tablename__ = 'check_referrals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    headuser = Column(String(120), nullable=True)
    is_checked = Column(Boolean, default=False)

    user = relationship('User')

class TetxStory(Base):
    __tablename__ = 'text_stories'
    story_id = Column(Integer, primary_key=True)
    text = Column(String(400), nullable=True)


class Advertise(Base):
    __tablename__ = 'advertises'
    user_id = Column(Integer, ForeignKey('users.user_id'))

    username = Column(String(50), nullable=True)
    title = Column(String(120), nullable=True)
    description = Column(String(120), nullable=True)
    status = Column(Boolean, default=False)
    accept_at = Column(DateTime, default=None)
    show = Column(Boolean ,default = False)
    show_at = Column(DateTime , default=None)

    user = relationship("User")