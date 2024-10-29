# Conversation Service

This service is responsible for handling the conversation between the candidate and the AI interviewer. It also handles STT (Speech to Text) and TTS (Text to Speech) services.

## Installation

1. Clone the repository

2. Rename the `.env.example` file to `.env` and update the values

```bash
cp .env.example .env
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Run the server

```bash
python -m app
```

## Documentation

After running the server, you can access the documentation at `http://localhost:8000/docs`.
