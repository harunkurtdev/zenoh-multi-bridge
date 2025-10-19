# Quick Start Guide

This guide will help you get up and running with the Zenoh Multi-Protocol Bridge in minutes.

## Starting the System

### Start All Services

```bash
cd zenoh-multi-bridge
docker-compose up -d
```

### Verify Services Are Running

```bash
docker-compose ps
```

All services should show "Up" status.

## Basic Usage Examples

### Example 1: MQTT to Zenoh Bridge

This example demonstrates how MQTT messages are automatically bridged to Zenoh.

**Step 1: Watch Zenoh Subscriber**

```bash
# Monitor the Zenoh subscriber logs
docker-compose logs -f zenoh-subscriber
```

**Step 2: Publish MQTT Message**

In another terminal:

```bash
# Publish to the MQTT bridge
mosquitto_pub -h localhost -p 1884 -t 'sensor/temperature' \
  -m '{"temp":25.5,"humidity":60,"timestamp":"2024-01-01T12:00:00Z"}'
```

**Expected Result**: You should see the message in the Zenoh subscriber logs with the key `mqtt/demo/sensor/temperature`.

### Example 2: Monitor Multi-Protocol Data Flow

**Step 1: Start Monitoring**

Open multiple terminals to monitor different parts of the system:

```bash
# Terminal 1: MQTT Subscriber
docker-compose logs -f mqtt-subscriber

# Terminal 2: Zenoh Subscriber
docker-compose logs -f zenoh-subscriber

# Terminal 3: MQTT Publisher (shows what's being sent)
docker-compose logs -f mqtt-publisher
```

**Observation**: The automatic MQTT publisher sends sensor data every second, and you can see it flowing through both MQTT and Zenoh subscribers.

### Example 3: ROS2 Integration

**Step 1: Check ROS2 Topics**

```bash
# Access the ROS2 container
docker exec -it ros2-humble bash

# Inside the container, list available topics
ros2 topic list

# Monitor a specific topic
ros2 topic echo /chatter
```

**Step 2: View Bridged Data**

The Zenoh-ROS2DDS bridge creates topics under the `/bot1` namespace. You should see topics like:

- `/chatter`
- `/bot1/*` (if any data is bridged to the bot1 namespace)

### Example 4: Node-RED Visualization

**Step 1: Access Node-RED**

Open your browser and navigate to [http://localhost:1880](http://localhost:1880)

**Step 2: View Existing Flows**

The Node-RED interface should display any pre-configured flows for monitoring MQTT and Zenoh data.

**Step 3: Create a Simple Dashboard**

1. Click the hamburger menu (☰) in the top right
2. Select "Dashboard" to open the dashboard view
3. Navigate to [http://localhost:1880/ui](http://localhost:1880/ui) to see your dashboard

## Using Test Scripts

The repository includes Python test scripts for direct Zenoh interaction.

### Setup (if not already done)

```bash
# Install Zenoh Python library
pip3 install zenoh
```

### Run Subscriber

```bash
# Subscribe to all Zenoh messages
python3 sub.py
```

### Run Publisher

In another terminal:

```bash
# Publish a message to Zenoh
python3 pub.py
```

You should see the message appear in the subscriber terminal.

## Web Interfaces Quick Access

| Interface | URL | Use Case |
|-----------|-----|----------|
| **Node-RED** | [http://localhost:1880](http://localhost:1880) | Create flows and visualizations |
| **Node-RED Dashboard** | [http://localhost:1880/ui](http://localhost:1880/ui) | View real-time data dashboards |
| **Zenoh REST API** | [http://localhost:8000](http://localhost:8000) | Query Zenoh router status |
| **MQTT Bridge API** | [http://localhost:8001](http://localhost:8001) | Monitor MQTT bridge status |
| **ROS2 Bridge API** | [http://localhost:8002](http://localhost:8002) | Check ROS2 bridge configuration |
| **Foxglove Studio** | [http://localhost:8765](http://localhost:8765) | Visualize ROS2 topics |

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f zenoh-router
docker-compose logs -f zenoh-mqtt-bridge
docker-compose logs -f zenoh-ros2dds-bridge
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart zenoh-router
```

### Stop Services

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop mqtt-publisher
```

### Start/Stop Individual Services

```bash
# Stop the automatic publisher
docker-compose stop mqtt-publisher

# Start it again
docker-compose start mqtt-publisher
```

## Testing Multi-Protocol Communication

### Test 1: MQTT → Zenoh Flow

```bash
# Terminal 1: Subscribe to Zenoh
python3 sub.py

# Terminal 2: Publish to MQTT (via bridge)
mosquitto_pub -h localhost -p 1884 -t 'test/data' -m 'Hello from MQTT!'
```

**Expected**: Message appears in Zenoh subscriber with key `mqtt/demo/test/data`

### Test 2: Cross-Protocol Monitoring

```bash
# Terminal 1: MQTT subscriber
mosquitto_sub -h localhost -p 1883 -t 'sensor/#' -v

# Terminal 2: Zenoh subscriber  
docker-compose logs -f zenoh-subscriber

# Terminal 3: Publish via MQTT bridge
mosquitto_pub -h localhost -p 1884 -t 'sensor/demo' -m '{"value":123}'
```

**Expected**: Message appears in both MQTT and Zenoh subscribers

### Test 3: ROS2 → Zenoh Bridge

```bash
# Terminal 1: Monitor Zenoh
python3 sub.py

# Terminal 2: Publish ROS2 message
docker exec -it ros2-humble bash
ros2 topic pub /test std_msgs/msg/String "data: 'Hello ROS2'" -1
```

**Expected**: Message bridged to Zenoh with key matching the ROS2 topic

## Quick Troubleshooting

### Services Not Starting

```bash
# Check which service failed
docker-compose ps

# View error logs
docker-compose logs [service-name]
```

### No Data Flowing

```bash
# Verify MQTT bridge is connected
docker-compose logs zenoh-mqtt-bridge | grep -i connect

# Verify ROS2 bridge is connected
docker-compose logs zenoh-ros2dds-bridge | grep -i connect

# Check Zenoh router
docker-compose logs zenoh-router
```

### Port Conflicts

```bash
# Check if ports are in use
netstat -tuln | grep -E '1880|1883|7447|8000'

# Modify docker-compose.yaml to use different ports if needed
```

## Next Steps

Now that you have the basic system running, explore more advanced features:

- **[Architecture Overview](../architecture/overview.md)**: Understand the system design
- **[Components](../components/zenoh-router.md)**: Deep dive into each component
- **[Configuration](../configuration/overview.md)**: Customize the system
- **[Testing](../usage/testing.md)**: Run comprehensive tests
- **[Use Cases](../use-cases/iot-robotics.md)**: Explore practical applications

## Stopping the System

When you're done:

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (removes persistent data)
docker-compose down -v
```

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](../troubleshooting.md) guide
2. Review service logs: `docker-compose logs [service-name]`
3. Open an issue on [GitHub](https://github.com/harunkurtdev/zenoh-multi-bridge/issues)
