import json

from pydantic import BaseModel


class IndividualInterviewReportResponse(BaseModel):
    question: str
    """The question."""

    answer: str
    """The answer."""

    feedback: str
    """The feedback."""

    score: float
    """The score."""

    def dict(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "feedback": self.feedback,
            "score": self.score,
        }

    def serialize(self) -> str:
        return json.dumps(self.dict())

    @classmethod
    def from_dict(cls, data):
        return cls(
            question=data["question"],
            answer=data["answer"],
            feedback=data["feedback"],
            score=data["score"],
        )


class InterviewReportResponse(BaseModel):
    interview_id: str
    """The interview ID."""

    feedbacks: list[IndividualInterviewReportResponse]
    """The individual feedback."""

    final_feedback: str
    """The overall feedback."""

    final_score: float
    """The final score."""

    def dict(self) -> dict:
        return {
            "interview_id": self.interview_id,
            "feedbacks": [feedback.dict() for feedback in self.feedbacks],
            "final_feedback": self.final_feedback,
            "final_score": self.final_score,
        }

    def serialize(self) -> str:
        return json.dumps(self.dict())

    @classmethod
    def from_dict(cls, data):
        return cls(
            interview_id=data["interview_id"],
            feedbacks=[
                IndividualInterviewReportResponse.from_dict(feedback)
                for feedback in data["feedbacks"]
            ],
            final_feedback=data["final_feedback"],
            final_score=data["final_score"],
        )

    @classmethod
    def from_serialized(cls, data):
        return cls.from_dict(json.loads(data))
