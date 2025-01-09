import logging

from app import INTERVIEW_QUEUE
from app.services.broker.events import EventService
from app.services.chat_history import ChatHistoryService
from app.services.feedback import FeedbackService
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

            messages = ChatHistoryService.get_messages(interview_id)
            if not messages or len(messages) == 0:
                return
            messages = messages[1:]  # Remove start message

            messages = [
                {"type": message.type, "message": message.content}
                for message in messages
            ]

            await EventService.publish(
                INTERVIEW_QUEUE,
                EventService.build_request_payload(
                    type=EventType.INTERVIEW_DETAILS,
                    data={
                        "interviewId": interview_id,
                        "transcript": messages,
                        "feedback": feedback.dict(),
                    },
                ),
            )

    @staticmethod
    async def respond_rpc(message):
        logging.info(f"Received RPC: {message}")

        return {"data": "Responding to RPC"}
