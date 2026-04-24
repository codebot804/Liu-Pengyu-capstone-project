from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from .database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    caption = Column(Text, default="")
    scene = Column(String, default="")
    weather = Column(String, default="")
    people = Column(String, default="")
    actions = Column(String, default="")
    objects = Column(String, default="")
    mood = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    embedding = relationship("Embedding", back_populates="photo", uselist=False, cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), unique=True, nullable=False)
    vector = Column(Text, nullable=False)

    photo = relationship("Photo", back_populates="embedding")
