from langchain_core.messages import MessageLikeRepresentation, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from app import GROQ_API_KEY, GROQ_MODEL, MODEL, USE_GROQ
from app.services.system_messages import interview_guidelines

_llm = (
    ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)
    if USE_GROQ
    else ChatOllama(model=MODEL)
)


class ChainService:
    """Service for handling chain operations."""

    def __init__(self, job_description: str, resume: str):
        self.messages: list[MessageLikeRepresentation] = [
            SystemMessage(content=interview_guidelines)
        ]

        self.add_job_description(job_description)
        self.add_resume(resume)
        self.finalize_prompt()

        self.prompt = None
        self.chain = None

    def add_message(self, message: MessageLikeRepresentation):
        """Add a message to the chain."""
        self.messages.append(message)

    def add_job_description(self, job_description: str):
        """Add the job description to the chain."""
        content = f"Job Description: {job_description}"
        self.add_message(SystemMessage(content=content))

    def add_resume(self, resume: str):
        """Add the resume to the chain."""
        content = f"Resume: {resume}"
        self.add_message(SystemMessage(content=content))

    def finalize_prompt(self):
        """Finalize the prompt for the conversation."""
        self.add_message(MessagesPlaceholder(variable_name="history"))
        self.add_message(("human", "{input}"))

    def get_prompt(self):
        """Get the prompt for the conversation."""
        if self.prompt:
            return self.prompt
        self.prompt = ChatPromptTemplate.from_messages(self.messages)
        return self.prompt

    def get_chain(self):
        """Get the chain for the conversation."""
        if self.chain:
            return self.chain
        self.chain = self.get_prompt() | _llm
        return self.chain
