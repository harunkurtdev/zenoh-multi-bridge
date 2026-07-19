FROM python:3.11-alpine

RUN pip install --no-cache-dir "paho-mqtt>=2.0.0"

WORKDIR /app
COPY recorder.py /app/recorder.py

ENV PYTHONUNBUFFERED=1

CMD ["python3", "recorder.py"]
