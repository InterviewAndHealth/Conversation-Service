FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

ENV HOST=0.0.0.0
ENV PORT=8000
ENV ENV=production

EXPOSE 8000

COPY ./app /code/app

CMD ["python", "-m", "app"]