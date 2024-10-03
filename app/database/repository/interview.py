from app.database import SessionLocal
from app.database.models import Interview


class InterviewRepository:
    def create(self, interview: Interview):
        db = SessionLocal()
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview

    def get(self, interview_id):
        db = SessionLocal()
        return db.query(Interview).filter(Interview.id == interview_id).first()
