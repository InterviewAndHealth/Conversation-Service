import time
from typing import List

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

_individual_feedback_message = """You are an experienced interviewer. You have taken the interview of the candidate based on the job description and resume. Now, you are assessing the candidate's response to a question. Provide feedback based on the job description and resume. Provide feedback like you are the real person who is talking to the candidate. Keep the feedback professional and detailed. Mention all positive and negative points in the feedback. Provide feedback in a way that the candidate can improve their response. Refer to candidate by You or Your in the feedback. Also provide a score to the candidate's response between 0 to 100 upto 4 decimal places."""

_overall_feedback_message = """You are an experienced interviewer. You have taken the interview of the candidate based on the job description and resume. Following are the feedbacks provided by you. Now, you are assessing the candidate's overall performance. Provide overall feedback keeping in mind all feedbacks provided by you. Keep feedback professional and detailed. Refer to candidate by You or Your in the feedback."""


class FeedbackResponse(BaseModel):
    feedback: str = Field(description="The feedback")
    score: float = Field(description="The score")


class OverallFeedbackResponse(BaseModel):
    feedback: str = Field(description="The feedback")


_feedback_request_parser = JsonOutputParser(pydantic_object=FeedbackResponse)
_overall_feedback_request_parser = JsonOutputParser(
    pydantic_object=OverallFeedbackResponse
)

_individual_prompt = PromptTemplate(
    template=_individual_feedback_message
    + "\n{format_instructions}\nJob Description: {job_description}\nResume: {resume}\nQuestion: {question}\nAnswer: {answer}",
    input_variables=["job_description", "resume", "question", "answer"],
    partial_variables={
        "format_instructions": _feedback_request_parser.get_format_instructions()
    },
)

_overall_prompt = PromptTemplate(
    template=_overall_feedback_message
    + "\n{format_instructions}\nJob Description: {job_description}\nResume: {resume}\nFeedbacks: {feedbacks}",
    input_variables=["job_description", "resume", "feedbacks"],
    partial_variables={
        "format_instructions": _overall_feedback_request_parser.get_format_instructions()
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

        if not is_interview_ended(elapsed_time, interview_id):
            raise BadRequestException400("Interview has not ended yet.")

        self.interview_id = interview_id

        self.job_description = RedisService.get_job_description(self.interview_id)
        self.resume = RedisService.get_resume(self.interview_id)

    def _generate_feedback(
        self, question: str, answer: str
    ) -> IndividualInterviewReportResponse:
        """Generate feedback based on the job description and resume."""
        chain = _individual_prompt | _llm | _feedback_request_parser

        feedback = ""
        score = 0.0

        while not feedback or score == 0.0:
            response = chain.invoke(
                {
                    "job_description": self.job_description,
                    "resume": self.resume,
                    "question": question,
                    "answer": answer,
                }
            )

            feedback = response.get("feedback", "")
            score = response.get("score", 0.0)

        return IndividualInterviewReportResponse(
            question=question,
            answer=answer,
            feedback=feedback,
            score=score,
        )

    def _get_overall_feedback(
        self, feedbacks: List[IndividualInterviewReportResponse]
    ) -> str:
        """Generate overall feedback based on the job description and resume."""
        chain = _overall_prompt | _llm | _overall_feedback_request_parser

        feedback = ""

        while not feedback:
            response = chain.invoke(
                {
                    "job_description": self.job_description,
                    "resume": self.resume,
                    "feedbacks": [feedback.feedback for feedback in feedbacks],
                }
            )

            feedback = response.get("feedback", "")

        return feedback

    def _get_feedback(self) -> InterviewReportResponse:
        """Generate feedback for all questions and answers."""
        messages = ChatHistoryService.get_messages(self.interview_id)

        if not messages or len(messages) == 0:
            raise NotFoundException404("Interview not found.")

        messages = messages[1:]

        # If number of messages < 2, then there are no questions and answers
        if len(messages) < 2:
            return InterviewReportResponse(
                interview_id=self.interview_id,
                feedbacks=[],
                final_feedback="",
                final_score=0.0,
            )

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

        overall_feedback = self._get_overall_feedback(feedbacks)

        return InterviewReportResponse(
            interview_id=self.interview_id,
            feedbacks=feedbacks,
            final_feedback=overall_feedback,
            final_score=final_score,
        )

    def generate_feedback(self) -> None:
        """Generate feedback for the question and answer."""
        feedback = RedisService.get_feedback(self.interview_id)

        if feedback:
            return

        feedback = self._get_feedback()
        RedisService.set_feedback(self.interview_id, feedback.dict())

    def get_feedback(self) -> InterviewReportResponse:
        """Get the feedback for the interview."""
        feedback = RedisService.get_feedback(self.interview_id)

        if feedback is not None:
            return InterviewReportResponse.from_dict(feedback)

        feedback = self._get_feedback()
        RedisService.set_feedback(self.interview_id, feedback.dict())
        return feedback
