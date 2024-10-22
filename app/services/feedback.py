import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app import GROQ_API_KEY, GROQ_MODEL, MODEL, USE_GROQ
from app.services.chat_history import ChatHistoryService
from app.services.redis import RedisService
from app.types.interview_report_response import (
    IndividualInterviewReportResponse,
    InterviewReportResponse,
)
from app.utils.errors.exceptions import BadRequestException400, NotFoundException404
from app.utils.timer import is_interview_ended

_system_message = """You are an experienced interviewer. You have taken the interview of the candidate based on the job description and resume. Now, you are assessing the candidate's response to a question. Provide feedback based on the job description and resume. Provide feedback like you are the real person who is talking to the candidate. Keep the feedback professional and detailed. Mention all positive and negative points in the feedback. Provide feedback in a way that the candidate can improve their response. Refer to candidate by You or Your in the feedback. Also provide a score to the candidate's response between 0 to 100 upto 4 decimal places."""


class FeedbackResponse(BaseModel):
    feedback: str = Field(
        description="The detailed feedback for the candidate's response."
    )
    score: float = Field(
        description="The score between 0 to 100 upto 4 decimal places."
    )


_feedback_request_parser = JsonOutputParser(pydantic_object=FeedbackResponse)

_prompt = PromptTemplate(
    template=_system_message
    + "\n{format_instructions}\nJob Description: {job_description}\nResume: {resume}\nQuestion: {question}\nAnswer: {answer}",
    input_variables=["job_description", "resume", "question", "answer"],
    partial_variables={
        "format_instructions": _feedback_request_parser.get_format_instructions()
    },
)

_llm = (
    ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)
    if USE_GROQ
    else ChatOllama(model=MODEL)
)


class FeedbackService:
    """Service for handling feedback operations."""

    def __init__(self, interview_id: str):
        start_time = RedisService.get_time(interview_id)
        if start_time is None:
            raise NotFoundException404("Interview not found.")

        start_time = float(start_time)
        elapsed_time = time.time() - start_time

        if not is_interview_ended(elapsed_time):
            raise BadRequestException400("Interview has not ended yet.")

        self.interview_id = interview_id

        self.job_description = RedisService.get_job_description(self.interview_id)
        self.resume = RedisService.get_resume(self.interview_id)

    def _generate_feedback(
        self, question: str, answer: str
    ) -> IndividualInterviewReportResponse:
        """Generate feedback based on the job description and resume."""
        chain = _prompt | _llm | _feedback_request_parser

        response = chain.invoke(
            {
                "job_description": self.job_description,
                "resume": self.resume,
                "question": question,
                "answer": answer,
            }
        )

        return IndividualInterviewReportResponse(
            question=question,
            answer=answer,
            feedback=response.get("feedback"),
            score=response.get("score"),
        )

    def _get_feedback(self) -> InterviewReportResponse:
        """Generate feedback for all questions and answers."""
        messages = ChatHistoryService.get_messages(self.interview_id)

        if not messages or len(messages) == 0:
            raise NotFoundException404("Interview not found.")

        messages = messages[1:]
        feedbacks = []

        for i in range(len(messages) // 2):
            index = i * 2
            question = messages[index].content
            answer = messages[index + 1].content

            if not question or not answer:
                continue

            feedback = self._generate_feedback(question, answer)
            feedbacks.append(feedback)

        final_score = sum([feedback.score for feedback in feedbacks]) / len(feedbacks)

        return InterviewReportResponse(
            interview_id=self.interview_id,
            feedbacks=feedbacks,
            score=final_score,
        )

    def get_feedback(self) -> InterviewReportResponse:
        """Get the feedback for the interview."""
        feedback = RedisService.get_feedback(self.interview_id)

        if feedback is not None:
            return InterviewReportResponse.from_dict(feedback)

        feedback = self._get_feedback()
        RedisService.set_feedback(self.interview_id, feedback.dict())
        return feedback
