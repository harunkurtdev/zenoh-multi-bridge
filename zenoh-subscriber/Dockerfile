FROM python:3.11-alpine

RUN apk add --no-cache gcc g++ musl-dev libgcc linux-headers curl
RUN pip install --upgrade pip
RUN pip install eclipse-zenoh
# RUN pip install eclipse-zenoh --no-binary :all: --config-settings build-args="--features=zenoh/shared-memory"

COPY subscriber.py /app/subscriber.py

