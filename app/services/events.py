import logging

from app.services.feedback import FeedbackService
from app.services.interview import InterviewService
from app.types.communications import EventType


class EventsService:
    @staticmethod
    async def handle_event(event):
        logging.info(f"Received event: {event}")

        if not event.get("type"):
            return

        if event["type"] == EventType.GENERATE_REPORT:
            if not event.get("data") or not event["data"].get("interview_id"):
                return
            interview_id = event["data"]["interview_id"]
            feedback = FeedbackService(interview_id).get_feedback()

            await InterviewService(interview_id).publish_feedback(feedback.dict())

    @staticmethod
    async def respond_rpc(message):
        logging.info(f"Received RPC: {message}")

        return {"data": "Responding to RPC"}
