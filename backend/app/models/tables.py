import uuid
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class TenantType(str, Enum):
    government = "government"
    business = "business"
    corporate = "corporate"


class NoticeStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    archived = "archived"


class NoticeSourceType(str, Enum):
    official_notice = "official_notice"
    advisory = "advisory"
    service_notice = "service_notice"


class FileType(str, Enum):
    pdf = "pdf"
    docx = "docx"
    jpg = "jpg"
    png = "png"
    text = "text"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[TenantType] = mapped_column(SqlEnum(TenantType), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    contact_email: Mapped[str | None] = mapped_column(String(100))
    office_address: Mapped[str | None] = mapped_column(Text)
    working_hours: Mapped[str | None] = mapped_column(String(100))
    allowed_source_types: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[NoticeSourceType] = mapped_column(SqlEnum(NoticeSourceType), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(100))
    publish_status: Mapped[NoticeStatus] = mapped_column(SqlEnum(NoticeStatus), default=NoticeStatus.draft)
    location: Mapped[str | None] = mapped_column(String(100))
    validity_start: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    validity_end: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    file_type: Mapped[FileType] = mapped_column(SqlEnum(FileType), nullable=False)
    original_file_path: Mapped[str | None] = mapped_column(Text)
    ocr_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    archived_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notices.id"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    phone_number: Mapped[str] = mapped_column(String(20), primary_key=True)
    last_known_location: Mapped[str | None] = mapped_column(String(100))
    subscribed_tenants: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    last_interaction_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_language: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LocationAlias(Base):
    __tablename__ = "location_aliases"

    alias: Mapped[str] = mapped_column(String(100), primary_key=True)
    canonical_location: Mapped[str] = mapped_column(String(100), nullable=False)


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str | None] = mapped_column(String(20), ForeignKey("users.phone_number"))
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_language: Mapped[str | None] = mapped_column(String(10))
    location: Mapped[str | None] = mapped_column(String(100))
    response_text: Mapped[str | None] = mapped_column(Text)
    response_language: Mapped[str | None] = mapped_column(String(10))
    response_type: Mapped[str | None] = mapped_column(String(50))
    retrieved_chunks: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UnansweredQuery(Base):
    __tablename__ = "unanswered_queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str | None] = mapped_column(String(20))
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_language: Mapped[str | None] = mapped_column(String(10))
    location: Mapped[str | None] = mapped_column(String(100))
    reason: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    notice_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("notices.id"))
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    target_location: Mapped[str | None] = mapped_column(String(100))
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
