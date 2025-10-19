# Zenoh-MQTT Bridge

The Zenoh-MQTT Bridge provides bidirectional protocol translation between MQTT and Zenoh, enabling IoT devices and applications using MQTT to seamlessly communicate with Zenoh-based systems.

## Overview

This bridge connects the MQTT and Zenoh worlds, translating messages in both directions while maintaining topic structure and message semantics.

```mermaid
graph LR
    subgraph "MQTT Domain"
        MP[MQTT Publisher] -->|MQTT| MB[MQTT Broker<br/>:1883]
        MB -->|MQTT| MS[MQTT Subscriber]
    end
    
    subgraph "Bridge"
        Bridge[Zenoh-MQTT Bridge<br/>:1884, :8001]
    end
    
    subgraph "Zenoh Domain"
        ZR[Zenoh Router<br/>:7447]
        ZS[Zenoh Subscriber]
    end
    
    MP -->|MQTT :1884| Bridge
    Bridge <-->|MQTT| MB
    Bridge <-->|Zenoh| ZR
    ZR -->|Zenoh| ZS
    
    classDef bridge fill:#fff3e0
    class Bridge bridge
```

## Key Features

### 1. Bidirectional Translation

- **MQTT → Zenoh**: MQTT messages are published to Zenoh with scoped keys
- **Zenoh → MQTT**: Zenoh messages are published to MQTT topics

### 2. Topic Mapping

- Configurable scope prefix (`mqtt/demo`)
- Topic filtering with allow/deny patterns
- Generalised subscriptions for wildcard topics

### 3. MQTT Server

Acts as an MQTT broker on port 1884:
- Clients can connect directly to the bridge
- Messages automatically forwarded to Zenoh

### 4. REST API

Provides monitoring and management via HTTP (port 8001)

## Configuration

### Current Configuration

Located at `zenoh-mqtt-bridge/config.json5`:

```json5
{
  mode: "client",
  connect: {
    endpoints: ["tcp/zenoh-router:7447"],
  },
  plugins: {
    rest: {
      http_port: 8000,
    },
    mqtt: {
      port: "0.0.0.0:1884",
      scope: "mqtt/demo",
      allow: ".*",
      deny: "^\\$SYS/.*|^private/.*",
      generalise_subs: [
        "sensor/*",
        "device/*",
        "data/*"
      ],
      generalise_pubs: [
        "sensor/**",
        "device/**",
        "data/**"
      ],
      tx_channel_size: 65536,
    }
  },
  plugins_loading: {
    enabled: true
  }
}
```

### Configuration Parameters

#### Mode
```json5
mode: "client"
```
Bridge connects as a client to the Zenoh router.

#### Zenoh Connection
```json5
connect: {
  endpoints: ["tcp/zenoh-router:7447"]
}
```
Specifies the Zenoh router endpoint.

#### MQTT Plugin Settings

**Port**
```json5
port: "0.0.0.0:1884"
```
The bridge listens for MQTT connections on port 1884.

**Scope**
```json5
scope: "mqtt/demo"
```
All MQTT topics are prefixed with this scope in Zenoh. For example:
- MQTT topic: `sensor/temperature`
- Zenoh key: `mqtt/demo/sensor/temperature`

**Allow/Deny Filters**
```json5
allow: ".*"
deny: "^\\$SYS/.*|^private/.*"
```
- `allow`: Accept all topics by default
- `deny`: Reject system topics (`$SYS/*`) and private topics

**Generalised Subscriptions**
```json5
generalise_subs: ["sensor/*", "device/*", "data/*"]
generalise_pubs: ["sensor/**", "device/**", "data/**"]
```
Optimizes subscription handling for wildcard topics.

**Buffer Size**
```json5
tx_channel_size: 65536
```
Transmission buffer size for high-throughput scenarios.

## Usage Examples

### Publishing MQTT Messages

#### Direct to Bridge

```bash
# Publish to bridge (port 1884)
mosquitto_pub -h localhost -p 1884 \
  -t 'sensor/temperature' \
  -m '{"temp":25.5,"humidity":60}'
```

This message will appear in Zenoh as: `mqtt/demo/sensor/temperature`

#### Via MQTT Broker

```bash
# Publish to Mosquitto (port 1883)
mosquitto_pub -h localhost -p 1883 \
  -t 'sensor/temperature' \
  -m '{"temp":25.5,"humidity":60}'
```

The bridge subscribes to the broker and forwards to Zenoh.

### Subscribing to MQTT Messages

```bash
# Subscribe via bridge
mosquitto_sub -h localhost -p 1884 -t 'sensor/#' -v

# Subscribe via broker
mosquitto_sub -h localhost -p 1883 -t 'sensor/#' -v
```

### Zenoh to MQTT Flow

Messages published to Zenoh keys matching the scope appear in MQTT:

```python
# Python Zenoh publisher
import zenoh

session = zenoh.open()
session.put("mqtt/demo/sensor/status", "online")
```

MQTT subscribers see this on topic: `sensor/status`

## Docker Configuration

```yaml
zenoh-mqtt-bridge:
  container_name: zenoh-mqtt-bridge
  image: eclipse/zenoh-bridge-mqtt:latest
  restart: unless-stopped
  depends_on:
    - mosquitto
    - zenoh-router
  ports:
    - "8001:8000"  # REST API
    - "1884:1884"  # MQTT port
  volumes:
    - ./zenoh-mqtt-bridge/config.json5:/etc/zenoh/config.json5
  environment:
    - RUST_LOG=debug
  networks:
    - zenoh-mqtt-net
  command: "-c /etc/zenoh/config.json5"
```

## Port Mappings

| Container Port | Host Port | Protocol | Purpose |
|----------------|-----------|----------|---------|
| 8000 | 8001 | HTTP | REST API |
| 1884 | 1884 | MQTT | MQTT server |

## Monitoring

### View Logs

```bash
# Real-time logs
docker-compose logs -f zenoh-mqtt-bridge

# Filter for errors
docker-compose logs zenoh-mqtt-bridge | grep -i error
```

### REST API

Check bridge status:

```bash
# Bridge information
curl http://localhost:8001/@/local/status

# List active subscriptions
curl http://localhost:8001/@/local/subscriptions
```

### Test Connectivity

```bash
# Test MQTT connection
mosquitto_pub -h localhost -p 1884 -t 'test' -m 'hello' -d

# Test from Zenoh side
python3 sub.py
```

## Topic Mapping Examples

### Example 1: Simple Topic

| MQTT Topic | Zenoh Key |
|------------|-----------|
| `sensor/temperature` | `mqtt/demo/sensor/temperature` |
| `device/status` | `mqtt/demo/device/status` |
| `data/metrics` | `mqtt/demo/data/metrics` |

### Example 2: Hierarchical Topics

| MQTT Topic | Zenoh Key |
|------------|-----------|
| `home/living/temp` | `mqtt/demo/home/living/temp` |
| `factory/line1/sensor3` | `mqtt/demo/factory/line1/sensor3` |

### Example 3: Wildcards

MQTT subscriptions with wildcards work seamlessly:

```bash
# Subscribe to all sensor topics
mosquitto_sub -h localhost -p 1884 -t 'sensor/#'
```

Receives all Zenoh messages under `mqtt/demo/sensor/*`

## Performance

### Throughput
- **10,000+ messages/second** typical
- **100,000+ messages/second** with tuning

### Latency
- **< 1ms** local bridge latency
- **< 5ms** end-to-end (MQTT → Zenoh)

### Resource Usage
- **Memory**: ~50 MB base
- **CPU**: < 2% idle, scales with message rate

## Troubleshooting

### Bridge Not Starting

```bash
# Check logs for errors
docker-compose logs zenoh-mqtt-bridge

# Verify Zenoh router is accessible
docker exec zenoh-mqtt-bridge ping -c 2 zenoh-router

# Test Zenoh connection
docker exec zenoh-mqtt-bridge nc -zv zenoh-router 7447
```

### Messages Not Forwarding

```bash
# Check if bridge receives MQTT messages
docker-compose logs zenoh-mqtt-bridge | grep -i "received\|publish"

# Verify topic matches allow/deny filters
# Check configuration: cat zenoh-mqtt-bridge/config.json5

# Test direct connection
mosquitto_pub -h localhost -p 1884 -t 'test' -m 'hello' -d
```

### High Latency

```bash
# Check buffer sizes in configuration
# Verify network connectivity
docker exec zenoh-mqtt-bridge ping -c 5 zenoh-router

# Monitor resource usage
docker stats zenoh-mqtt-bridge
```

## Advanced Configuration

### Custom Topic Mapping

Modify the scope for different key namespaces:

```json5
{
  plugins: {
    mqtt: {
      scope: "iot/sensors",  // Custom scope
      // MQTT 'temp' becomes 'iot/sensors/temp' in Zenoh
    }
  }
}
```

### Multiple Bridges

Run multiple bridge instances with different scopes:

```yaml
zenoh-mqtt-bridge-1:
  volumes:
    - ./bridge1-config.json5:/etc/zenoh/config.json5
  ports:
    - "1884:1884"

zenoh-mqtt-bridge-2:
  volumes:
    - ./bridge2-config.json5:/etc/zenoh/config.json5
  ports:
    - "1885:1884"
```

### QoS Mapping

MQTT QoS levels are handled:
- **QoS 0**: Fire and forget (Zenoh default)
- **QoS 1**: At least once (Zenoh with reliability)
- **QoS 2**: Exactly once (Not fully supported)

## Best Practices

1. **Use Meaningful Scopes**: Choose scopes that reflect your data organization
2. **Filter Topics**: Use allow/deny to reduce unnecessary traffic
3. **Monitor Logs**: Check for dropped messages or errors
4. **Test Bidirectionally**: Verify both MQTT→Zenoh and Zenoh→MQTT
5. **Tune Buffer Sizes**: Adjust `tx_channel_size` for your throughput needs

## Security Considerations

- Bridge has no authentication by default
- Consider using MQTT authentication on broker
- Use network isolation (Docker networks)
- For production, implement TLS/SSL

## See Also

- [MQTT Broker](mqtt-broker.md)
- [Zenoh Router](zenoh-router.md)
- [Configuration Guide](../configuration/mqtt-bridge.md)
- [Eclipse Zenoh MQTT Bridge](https://github.com/eclipse-zenoh/zenoh-plugin-mqtt)
