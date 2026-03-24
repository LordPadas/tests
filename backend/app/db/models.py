from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    name = Column(String)
    owner = Column(String)
    mime_type = Column(String)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    latest_version_id = Column(Integer, ForeignKey("file_versions.id"))
    latest_version = relationship("FileVersion", back_populates="file")


class FileVersion(Base):
    __tablename__ = "file_versions"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    version_number = Column(Integer)
    created_at = Column(DateTime)
    hash = Column(String)
    file = relationship("File", back_populates="latest_version")


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    file_version_id = Column(Integer, ForeignKey("file_versions.id"))
    chunk_index = Column(Integer)
    text_chunk = Column(String)
    embedding_vector = Column(String)  # placeholder for pgvector/vector data


class IndexingJob(Base):
    __tablename__ = "indexing_jobs"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String)
    description = Column(String)


class AccessPolicy(Base):
    __tablename__ = "access_policies"
    id = Column(Integer, primary_key=True)
    policy_name = Column(String)
    read_only = Column(String)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    target_file_id = Column(Integer, ForeignKey("files.id"))
    source = Column(String)
    detail = Column(String)
    timestamp = Column(DateTime)
