import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(128), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Instance(Base):
    __tablename__ = "instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False)
    phone_number = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    session_encrypted = Column(Text, nullable=True)
    phone_code_hash = Column(String(64), nullable=True)
    twofa_password_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    webhook = relationship("Webhook", uselist=False, back_populates="instance", cascade="all, delete-orphan")


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id"), nullable=False, unique=True)
    url = Column(String(2048), nullable=False)
    secret = Column(String(64), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    max_retries = Column(Integer, nullable=False, default=3)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    instance = relationship("Instance", back_populates="webhook")
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    attempt_count = Column(Integer, nullable=False, default=0)
    last_status_code = Column(Integer, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    webhook = relationship("Webhook", back_populates="deliveries")
