import asyncio
import logging

from app import (
    INTERVIEW_DURATION,
    INTERVIEW_QUEUE,
    INTERVIEW_RPC,
    JOB_QUEUE,
    JOB_RPC,
    SCHEDULER_QUEUE,
    USER_RPC,
)
from app.services.broker.events import EventService
from app.services.broker.rpc import RPCService
from app.services.chat_history import ChatHistoryService
from app.services.redis import RedisService
from app.types.communications import EventType, RPCPayloadType
from app.utils.errors.exceptions import BadRequestException400, NotFoundException404
from app.utils.pdf_text import fetch_pdf_text


class InterviewService:
    """Service for handling interview related operations"""

    def __init__(self, interview_id: str, user_id: str = None, is_job: bool = False):
        self.interview_id = interview_id
        self.user_id = user_id
        self.is_job = is_job

        self.job_description = None
        self.resume = None

    async def initialize(self) -> bool:
        """Initialize the interview details"""
        if not all([self.interview_id, self.user_id]):
            logging.error("Interview ID or User ID not provided.")
            raise BadRequestException400("Interview ID or User ID not provided.")

        if self.user_id == "user_id":
            data = await self._get_dummy_data()
        elif self.is_job:
            data = await self._get_data_for_job_interview()
        else:
            data = await self._get_data_for_normal_interview()

        if not data:
            return False

        logging.info(f"Data: {data}")

        if self.user_id != data.get("user_id"):
            logging.error(
                f"User is not authorized for this interview: {self.interview_id}"
            )
            raise BadRequestException400("User is not authorized for this interview.")

        if data.get("resume_url"):
            resume = await fetch_pdf_text(data.get("resume_url"))
            logging.info(f"Resume: {resume}")
            if not resume:
                logging.error(
                    f"Error fetching resume for interview: {self.interview_id}"
                )
                raise NotFoundException404("Error processing the resume.")

            data["resume"] = resume

        self.job_description = data.get("job_description")
        self.resume = data.get("resume")

        self.set_details()

        return True

    async def _get_data_for_normal_interview(self):
        logging.info(f"Fetching data for normal interview: {self.interview_id}")
        interview_details, resume_url = await asyncio.gather(
            RPCService.request(
                INTERVIEW_RPC,
                RPCService.build_request_payload(
                    type=RPCPayloadType.GET_INTERVIEW_DETAILS,
                    data={"interviewId": self.interview_id},
                ),
            ),
            RPCService.request(
                USER_RPC,
                RPCService.build_request_payload(
                    type=RPCPayloadType.GET_USER_RESUME,
                    data={"userId": self.user_id},
                ),
            ),
        )

        if not interview_details or not resume_url:
            logging.error(f"Interview not found: {self.interview_id}")
            raise NotFoundException404("Interview not found.")

        return {
            "user_id": interview_details.get("data").get("userid"),
            "job_description": interview_details.get("data").get("jobdescription"),
            "resume_url": resume_url.get("data"),
        }

    async def _get_data_for_job_interview(self):
        logging.info(f"Fetching data for job interview: {self.interview_id}")
        details = await RPCService.request(
            JOB_RPC,
            RPCService.build_request_payload(
                type=RPCPayloadType.GET_APPLICANT_DETAILS_FOR_JOB_INTERVIEW,
                data={"interview_id": self.interview_id},
            ),
        )

        if not details:
            logging.error(f"Interview not found: {self.interview_id}")
            raise NotFoundException404("Interview not found.")

        job_description = f"""
        Job Title: {details.get("job").get("job_title")}
        Job Experience: {details.get("job").get("job_experience")}
        Job Type: {details.get("job").get("job_type")}
        Required Skills: {", ".join(details.get("job").get("required_skills"))}

        Job Description: 
        
        {details.get("job").get("job_description")}
        """

        return {
            "user_id": details.get("application").get("applicant_user_id"),
            "job_description": job_description,
            "resume_url": details.get("resume_url"),
        }

    async def _get_dummy_data(self):
        logging.info(f"Fetching dummy data for interview: {self.interview_id}")
        return {
            "user_id": "user_id",
            "job_description": "We are looking for a frontend developer. The candidate should have experience with React.",
            "resume": "Gopal Saraf\nFrontend Developer",
        }

    def set_details(self):
        """Set the interview details in redis"""
        RedisService.set_user(self.interview_id, self.user_id)
        RedisService.set_job_description(self.interview_id, self.job_description)
        RedisService.set_resume(self.interview_id, self.resume)
        RedisService.set_interview_type(
            self.interview_id,
            (
                RedisService.InterviewType.JOB
                if self.is_job
                else RedisService.InterviewType.NORMAL
            ),
        )

    def clear_details(self):
        """Clear the interview details from redis"""
        pass

    def get_conversation(self):
        """Get the conversation transcript"""
        messages = ChatHistoryService.get_messages(self.interview_id)

        if not messages or len(messages) == 0:
            return None

        return messages[1:]  # Remove start message

    async def publish_feedback(self, feedback):
        """Publish the feedback to the broker"""
        messages = self.get_conversation()
        messages = [
            {"type": message.type, "message": message.content} for message in messages
        ]

        interview_type = RedisService.get_interview_type(self.interview_id)

        await EventService.publish(
            (
                INTERVIEW_QUEUE
                if interview_type == RedisService.InterviewType.NORMAL
                else JOB_QUEUE
            ),
            EventService.build_request_payload(
                type=EventType.INTERVIEW_DETAILS,
                data={
                    "interviewId": self.interview_id,
                    "transcript": messages,
                    "feedback": feedback,
                },
            ),
        )

    async def publish_interview_started(self):
        """Publish the interview start event to the broker"""
        interview_type = RedisService.get_interview_type(self.interview_id)

        await asyncio.gather(
            EventService.publish(
                (
                    INTERVIEW_QUEUE
                    if interview_type == RedisService.InterviewType.NORMAL
                    else JOB_QUEUE
                ),
                EventService.build_request_payload(
                    type=EventType.INTERVIEW_STARTED,
                    data={"interviewId": self.interview_id},
                ),
            ),
            EventService.publish(
                SCHEDULER_QUEUE,
                EventService.build_request_payload(
                    type=EventType.SCHEDULE_EVENT,
                    data={
                        "id": f"interview_completed_{self.interview_id}",
                        "seconds": INTERVIEW_DURATION * 60,
                        "service": (
                            INTERVIEW_QUEUE
                            if interview_type == RedisService.InterviewType.NORMAL
                            else JOB_QUEUE
                        ),
                        "type": EventType.INTERVIEW_COMPLETED,
                        "data": {"interviewId": self.interview_id},
                    },
                ),
            ),
        )

    async def publish_interview_completed(self):
        """Publish the interview completion event to the broker"""
        interview_type = RedisService.get_interview_type(self.interview_id)

        await EventService.publish(
            SCHEDULER_QUEUE,
            EventService.build_request_payload(
                type=EventType.SCHEDULE_EVENT,
                data={
                    "id": f"interview_completed_{self.interview_id}",
                    "seconds": 1,
                    "service": (
                        INTERVIEW_QUEUE
                        if interview_type == RedisService.InterviewType.NORMAL
                        else JOB_QUEUE
                    ),
                    "type": EventType.INTERVIEW_COMPLETED,
                    "data": {"interviewId": self.interview_id},
                },
            ),
        )
