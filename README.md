# Conversation Service

This service is responsible for handling the conversation between the candidate and the AI interviewer. It also handles STT (Speech to Text) and TTS (Text to Speech) services.

## Installation

1. Clone the repository
2. Start the docker container

```bash
docker compose up -d
```

3. Rename the `.env.example` file to `.env` and update the values

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

After running the server, you can access the documentation at `http://localhost:8002/docs`.

## Database

For Database, you can access the admin panel at `http://localhost:5050` with the following credentials:

- Email: `admin@admin.com`
- Password: `admin`

## Redis

For Redis, you can access the redis web UI at `http://localhost:6380`.

## RabbitMQ

For RabbitMQ, you can access the RabbitMQ web UI at `http://localhost:15672` with the following credentials:

- Username: `guest`
- Password: `guest`
