FROM python:3.11-alpine

RUN pip install --no-cache-dir "paho-mqtt>=2.0.0"

WORKDIR /app
COPY robot_simulator.py teleop.py fleet_monitor.py /app/

ENV PYTHONUNBUFFERED=1

# Default: run the simulator. Override `command` for teleop/monitor.
CMD ["python3", "robot_simulator.py"]
