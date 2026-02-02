from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .database import Base

def get_ist_time():
    # Helper to get current time in IST (Naive for SQLite storage ease)
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user") # 'user' or 'authority'

    posts = relationship("Post", back_populates="owner")
    aid_requests = relationship("AidRequest", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True) # Using string ID to match frontend's "p_..." format if needed, or we can use UUID
    location = Column(String)
    caption = Column(String)
    description = Column(Text)
    image_data = Column(Text) # Storing base64 string for simplicity in hackathon
    
    created_at = Column(DateTime, default=get_ist_time)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # "AI" fields
    risk_score = Column(Integer, default=0)
    
    # Community interaction
    likes = Column(Integer, default=0)
    status = Column(String, default="Open") # Open, Resolved, Dismissed
    
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=get_ist_time)
    post_id = Column(String, ForeignKey("posts.id"))
    
    post = relationship("Post", back_populates="comments")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    # Geo-coordinates for distance sorting
    lat = Column(Float)
    lon = Column(Float)
    
    title = Column(String)
    message = Column(String)
    severity = Column(String) # High, Medium, Low
    alert_type = Column(String) # Cyclone, Algal Bloom, etc.
    source = Column(String, default="Unknown") # e.g. Satellite, IoT
    created_at = Column(DateTime, default=get_ist_time)

class AidRequest(Base):
    __tablename__ = "aid_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=get_ist_time)
    
    # New fields for Advanced Hub
    description = Column(String, default="")
    needs = Column(String, default="General") # Food, Medical, Rescue
    urgency = Column(String, default="Medium") # High, Medium, Low
    urgency_score = Column(Integer, default=0) # AI calculated score (0-100)
    status = Column(String, default="Pending") # Pending, In Progress, Resolved
    contact = Column(String, default="")
    location = Column(String, default="Unknown")

    user = relationship("User", back_populates="aid_requests")
