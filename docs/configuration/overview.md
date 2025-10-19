# Configuration Overview

This guide provides an overview of configuration options for the Zenoh Multi-Protocol Bridge system.

## Configuration Files

The system uses multiple configuration files:

| File | Purpose | Format |
|------|---------|--------|
| `docker-compose.yaml` | Service orchestration | YAML |
| `zenoh-mqtt-bridge/config.json5` | MQTT bridge settings | JSON5 |
| `zenoh-ros2dds-bridge/config.json5` | ROS2 bridge settings | JSON5 |
| `mosquitto/config/mosquitto.conf` | MQTT broker config | INI-style |

## Quick Configuration

### Changing Ports

Edit `docker-compose.yaml`:

```yaml
services:
  service-name:
    ports:
      - "NEW_HOST_PORT:CONTAINER_PORT"
```

### Adjusting Log Levels

```yaml
environment:
  - RUST_LOG=info  # Options: error, warn, info, debug, trace
```

### Modifying Bridge Scopes

Edit `zenoh-mqtt-bridge/config.json5`:

```json5
{
  plugins: {
    mqtt: {
      scope: "your/custom/scope"
    }
  }
}
```

## See Also

- [MQTT Bridge Configuration](mqtt-bridge.md)
- [ROS2 Bridge Configuration](ros2-bridge.md)
- [Docker Compose Configuration](docker-compose.md)
