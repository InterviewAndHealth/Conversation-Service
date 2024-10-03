from sqlalchemy import JSON, TIMESTAMP, Column, String, text

from app.database import Base, engine


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, index=True)
    conversations = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=text("now()"))


Interview.metadata.create_all(engine)
