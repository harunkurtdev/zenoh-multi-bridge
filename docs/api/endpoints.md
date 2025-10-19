# API Endpoints

This page provides a comprehensive reference for all REST API endpoints available in the Zenoh Multi-Protocol Bridge system.

## Overview

The system exposes multiple REST APIs for monitoring, management, and interaction:

| Service | Port | Base URL | Purpose |
|---------|------|----------|---------|
| Zenoh Router | 8000 | http://localhost:8000 | Router status and operations |
| MQTT Bridge | 8001 | http://localhost:8001 | Bridge monitoring and config |
| ROS2 Bridge | 8002 | http://localhost:8002 | ROS2 bridge management |

## Zenoh Router API

### Base URL
```
http://localhost:8000
```

### Get Router Status

**Endpoint:** `GET /@/router/local`

**Description:** Retrieve information about the local Zenoh router.

**Example:**
```bash
curl http://localhost:8000/@/router/local
```

**Response:**
```json
{
  "zid": "...",
  "links": [...],
  "locators": [...]
}
```

### Publish Data

**Endpoint:** `PUT /<key>`

**Description:** Publish data to a Zenoh key.

**Example:**
```bash
curl -X PUT http://localhost:8000/demo/sensor/temp \
  -H 'Content-Type: application/json' \
  -d '{"temperature": 25.5, "unit": "celsius"}'
```

### Query Data

**Endpoint:** `GET /<key-expression>`

**Description:** Query data matching a key expression.

**Example:**
```bash
# Query specific key
curl http://localhost:8000/demo/sensor/temp

# Query with wildcard
curl http://localhost:8000/demo/sensor/*
```

### Subscribe via SSE

**Endpoint:** `GET /<key-expression>`

**Headers:** `Accept: text/event-stream`

**Description:** Subscribe to updates using Server-Sent Events.

**Example:**
```bash
curl http://localhost:8000/demo/sensor/* \
  -H 'Accept: text/event-stream'
```

## MQTT Bridge API

### Base URL
```
http://localhost:8001
```

### Get Bridge Status

**Endpoint:** `GET /@/local/status`

**Description:** Get the current status of the MQTT bridge.

**Example:**
```bash
curl http://localhost:8001/@/local/status
```

### List Subscriptions

**Endpoint:** `GET /@/local/subscriptions`

**Description:** List active MQTT subscriptions.

**Example:**
```bash
curl http://localhost:8001/@/local/subscriptions
```

### Get Configuration

**Endpoint:** `GET /@/local/config`

**Description:** Retrieve the current bridge configuration.

**Example:**
```bash
curl http://localhost:8001/@/local/config
```

## ROS2 Bridge API

### Base URL
```
http://localhost:8002
```

### Get Bridge Status

**Endpoint:** `GET /@/local/status`

**Description:** Get the current status of the ROS2 bridge.

**Example:**
```bash
curl http://localhost:8002/@/local/status
```

### List Active Topics

**Endpoint:** `GET /@/local/topics`

**Description:** List ROS2 topics being bridged.

**Example:**
```bash
curl http://localhost:8002/@/local/topics
```

### Get Configuration

**Endpoint:** `GET /@/local/config`

**Description:** Retrieve the current ROS2 bridge configuration.

**Example:**
```bash
curl http://localhost:8002/@/local/config
```

## Common Patterns

### Health Check

Check if services are responsive:

```bash
# Check all services
curl http://localhost:8000/@/router/local
curl http://localhost:8001/@/local/status
curl http://localhost:8002/@/local/status
```

### Publish-Subscribe Pattern

```bash
# Terminal 1: Subscribe
curl http://localhost:8000/test/* \
  -H 'Accept: text/event-stream'

# Terminal 2: Publish
curl -X PUT http://localhost:8000/test/message \
  -d 'Hello World'
```

### Query Pattern

```bash
# Store data
curl -X PUT http://localhost:8000/data/sensor1 -d '{"temp": 22}'
curl -X PUT http://localhost:8000/data/sensor2 -d '{"temp": 24}'

# Query all sensors
curl http://localhost:8000/data/*
```

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed successfully |
| 404 | Not Found | Key or endpoint doesn't exist |
| 500 | Server Error | Check service logs |
| 503 | Service Unavailable | Service is starting or down |

### Error Response Format

```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Authentication

Currently, the REST APIs do not require authentication. For production deployments:

1. Use a reverse proxy (nginx, traefik)
2. Implement authentication at the proxy level
3. Restrict network access to trusted clients
4. Consider TLS/SSL for encryption

## Rate Limiting

No rate limiting is implemented by default. Consider implementing rate limiting at the proxy level for production use.

## Examples

### Monitor Sensor Data

```bash
#!/bin/bash
# monitor-sensors.sh

while true; do
  echo "=== Sensor Status ==="
  curl -s http://localhost:8000/mqtt/demo/sensor/* | jq '.'
  sleep 5
done
```

### Publish Periodic Updates

```bash
#!/bin/bash
# publish-data.sh

while true; do
  TEMP=$((20 + RANDOM % 10))
  curl -X PUT http://localhost:8000/demo/temperature \
    -H 'Content-Type: application/json' \
    -d "{\"value\": $TEMP, \"timestamp\": \"$(date -Iseconds)\"}"
  echo "Published: $TEMP"
  sleep 1
done
```

## See Also

- [REST APIs Documentation](rest-apis.md)
- [Testing Guide](../usage/testing.md)
- [Troubleshooting](../troubleshooting.md)
