# Data Flow

Understanding how data flows through the Zenoh Multi-Protocol Bridge system.

## Multi-Protocol Flow

Data flows seamlessly between MQTT, Zenoh, and ROS2:

```mermaid
sequenceDiagram
    participant MQTT as MQTT Publisher
    participant Bridge as MQTT Bridge
    participant Router as Zenoh Router
    participant ROS2Bridge as ROS2 Bridge
    participant ROS2 as ROS2 Node
    
    MQTT->>Bridge: MQTT Publish
    Bridge->>Router: Zenoh Put
    Router->>ROS2Bridge: Zenoh Sample
    ROS2Bridge->>ROS2: ROS2 Publish
```

See the [Architecture Overview](overview.md) for more details.
