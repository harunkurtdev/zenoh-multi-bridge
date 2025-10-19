# REST APIs

Detailed documentation for the REST APIs provided by each component of the Zenoh Multi-Protocol Bridge.

## API Overview

Each major component exposes a REST API for monitoring and management:

- **Zenoh Router**: Core routing operations and monitoring
- **MQTT Bridge**: Bridge status and MQTT-specific operations
- **ROS2 Bridge**: ROS2 integration status and topic management

## Authentication & Security

!!! warning "Production Security"
    The default configuration does not include authentication. For production deployments:
    
    - Use a reverse proxy with authentication (nginx, traefik)
    - Implement TLS/SSL encryption
    - Restrict network access using firewalls
    - Consider API key or OAuth2 authentication

## Content Types

All APIs support the following content types:

- **Request**: `application/json`, `text/plain`
- **Response**: `application/json`, `text/event-stream` (for subscriptions)

## See Also

- [API Endpoints](endpoints.md) - Complete endpoint reference
- [Usage Examples](../usage/testing.md) - Practical API usage examples
