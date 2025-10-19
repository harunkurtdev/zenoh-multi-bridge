# Installation

This guide will walk you through the installation process of the Zenoh Multi-Protocol Bridge system.

## Quick Installation

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/harunkurtdev/zenoh-multi-bridge.git
cd zenoh-multi-bridge

# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps
```

That's it! All services should now be running.

## Step-by-Step Installation

### 1. Clone the Repository

First, clone the project repository from GitHub:

```bash
git clone https://github.com/harunkurtdev/zenoh-multi-bridge.git
cd zenoh-multi-bridge
```

### 2. Review Configuration Files

Before starting the services, you may want to review the configuration files:

```bash
# View the main docker-compose configuration
cat docker-compose.yaml

# View MQTT bridge configuration
cat zenoh-mqtt-bridge/config.json5

# View ROS2 bridge configuration
cat zenoh-ros2dds-bridge/config.json5
```

Configuration details are explained in the [Configuration](../configuration/overview.md) section.

### 3. Build Custom Images

Some services use custom Docker images that need to be built:

```bash
# Build all custom images
docker-compose build

# Or build specific services
docker-compose build ros2-humble
docker-compose build zenoh-ros2dds-bridge
docker-compose build node-red
docker-compose build zenoh-subscriber
```

### 4. Start the Services

Start all services in detached mode:

```bash
docker-compose up -d
```

This command will:

- Pull required Docker images (if not already present)
- Build custom images (if needed)
- Create a dedicated network (`zenoh-mqtt-net`)
- Start all services in the background

### 5. Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

You should see all services in the "Up" state:

```
NAME                    IMAGE                              STATUS
mosquitto               eclipse-mosquitto:latest           Up
zenoh-router            eclipse/zenoh:latest               Up
ros2-humble             zenoh-multi-bridge-ros2-humble     Up
zenoh-ros2dds-bridge    zenoh-multi-bridge-zenoh-ros2...   Up
ros2-humble-pub         zenoh-multi-bridge-ros2-humble     Up
node-red                zenoh-multi-bridge-node-red        Up
zenoh-mqtt-bridge       eclipse/zenoh-bridge-mqtt:latest   Up
mqtt-publisher          eclipse-mosquitto:latest           Up
mqtt-subscriber         eclipse-mosquitto:latest           Up
zenoh-subscriber        zenoh-multi-bridge-zenoh-sub...    Up
```

### 6. Check Service Logs

Monitor the logs to ensure everything is working correctly:

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f zenoh-router
docker-compose logs -f zenoh-mqtt-bridge
docker-compose logs -f zenoh-ros2dds-bridge
docker-compose logs -f mqtt-publisher
```

Press `Ctrl+C` to stop following logs.

## Accessing Web Interfaces

Once all services are running, you can access the web interfaces:

| Service | URL | Description |
|---------|-----|-------------|
| Node-RED | [http://localhost:1880](http://localhost:1880) | Visual flow editor and dashboard |
| Zenoh REST API | [http://localhost:8000](http://localhost:8000) | Zenoh router REST interface |
| MQTT Bridge API | [http://localhost:8001](http://localhost:8001) | MQTT bridge REST API |
| ROS2 Bridge API | [http://localhost:8002](http://localhost:8002) | ROS2 bridge REST API |
| Foxglove Studio | [http://localhost:8765](http://localhost:8765) | ROS2 web visualization |

## Testing the Installation

### Test MQTT Communication

Test MQTT message publishing and subscribing:

```bash
# Subscribe to MQTT topic (in one terminal)
docker exec -it mqtt-subscriber mosquitto_sub -h mosquitto -t 'test/topic' -v

# Publish a message (in another terminal)
docker exec -it mosquitto mosquitto_pub -h mosquitto -t 'test/topic' -m 'Hello MQTT!'
```

### Test Zenoh Communication

If you have Python and Zenoh installed on your host:

```bash
# Terminal 1: Subscribe to Zenoh
python3 sub.py

# Terminal 2: Publish to Zenoh
python3 pub.py
```

### Test Multi-Protocol Bridge

Publish an MQTT message and verify it reaches Zenoh:

```bash
# Terminal 1: Watch Zenoh subscriber logs
docker-compose logs -f zenoh-subscriber

# Terminal 2: Publish MQTT message to bridge
mosquitto_pub -h localhost -p 1884 -t 'sensor/test' -m '{"value": 42}'
```

You should see the message appear in the Zenoh subscriber logs.

## Troubleshooting Installation

### Containers Not Starting

If containers fail to start, check the logs:

```bash
docker-compose logs [service-name]
```

Common issues:

1. **Port conflicts**: Ensure required ports are not in use
2. **Insufficient resources**: Docker needs adequate CPU and memory
3. **Permission issues**: Ensure your user is in the `docker` group

### Port Already in Use

If you get a port conflict error:

```bash
# Find which process is using the port
lsof -i :PORT_NUMBER

# Stop the conflicting process or modify docker-compose.yaml
# to use different host ports
```

### Docker Permission Denied

If you get permission errors:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### Services Not Connecting

If services can't connect to each other:

1. Verify the network is created:
   ```bash
   docker network ls | grep zenoh-mqtt-net
   ```

2. Check container DNS resolution:
   ```bash
   docker exec zenoh-mqtt-bridge ping -c 2 zenoh-router
   ```

## Updating the Installation

To update to the latest version:

```bash
# Stop all services
docker-compose down

# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Start services
docker-compose up -d
```

## Uninstalling

To completely remove the installation:

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove Docker images
docker-compose down --rmi all

# Remove the repository
cd ..
rm -rf zenoh-multi-bridge
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Learn how to use the system
- [Configuration](../configuration/overview.md) - Customize the setup
- [Testing](../usage/testing.md) - Run comprehensive tests
