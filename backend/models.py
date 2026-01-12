from sqlalchemy import Column, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Persona(Base):
    __tablename__="personas"
    
    id=Column(String,primary_key=True,default=generate_uuid)
    name=Column(String,nullable=False)
    system_prompt=Column(Text,nullable=False)
    provider=Column(String,nullable=False)  
    model_id=Column(String,nullable=False)  
    temperature=Column(Float,default=1.0) 
    created_at=Column(DateTime,default=datetime.utcnow)

class Conversation(Base):
    __tablename__="conversations"
    
    id=Column(String,primary_key=True,default=generate_uuid)
    title=Column(String,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    messages=relationship("Message",back_populates="conversation",cascade="all, delete-orphan")


class Message(Base):
    __tablename__="messages"
    
    id=Column(String,primary_key=True,default=generate_uuid)
    conversation_id=Column(String,ForeignKey("conversations.id"))
    role=Column(String,nullable=False) 
    # format: {"stage1": [...], "stage2": [...], "stage3": [...]}
    # stage1:individual answers, stage2: critiques of each other(persona a will get a[j] where j!=i), stage3: chairmain comes into play
    # and produce final synthesized answer based on stage1 and stage2
    content=Column(JSON,nullable=False)
    timestamp=Column(DateTime,default=datetime.utcnow)
    conversation=relationship("Conversation",back_populates="messages")