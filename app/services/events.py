from app.services.feedback import FeedbackService
from app.types.communications import EventType


class EventsService:
    @staticmethod
    async def handle_event(event):
        if not event.get("type"):
            return

        if event["type"] == EventType.GENERATE_REPORT:
            if not event.get("data") or not event["data"].get("interview_id"):
                return
            FeedbackService(event["data"]["interview_id"]).generate_feedback()

    @staticmethod
    async def respond_rpc(message):
        print(f"Received RPC: {message}")
        return {"data": "Responding to RPC"}
