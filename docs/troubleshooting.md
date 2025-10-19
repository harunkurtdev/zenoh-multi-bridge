# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Zenoh Multi-Protocol Bridge.

## General Troubleshooting Steps

### 1. Check Service Status

```bash
# List all containers and their status
docker-compose ps

# Check if all services are running
docker ps --filter "name=zenoh" --filter "name=mqtt" --filter "name=ros2" --filter "name=node-red"
```

### 2. View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f zenoh-router
docker-compose logs -f zenoh-mqtt-bridge
docker-compose logs -f zenoh-ros2dds-bridge
```

### 3. Verify Network Connectivity

```bash
# Check Docker network
docker network inspect zenoh-mqtt-net

# Test connectivity between services
docker exec zenoh-mqtt-bridge ping -c 2 zenoh-router
docker exec zenoh-ros2dds-bridge ping -c 2 zenoh-router
```

## Common Issues

### Services Won't Start

#### Issue: Port Already in Use

**Symptoms:**
```
Error: Bind for 0.0.0.0:1883 failed: port is already allocated
```

**Solution:**
```bash
# Find process using the port
lsof -i :1883
# or
netstat -tuln | grep 1883

# Stop the conflicting process or change port in docker-compose.yaml
# Example: Change host port mapping
ports:
  - "1884:1883"  # Maps host:1884 to container:1883
```

#### Issue: Docker Permission Denied

**Symptoms:**
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group membership (or log out and back in)
newgrp docker

# Verify
docker ps
```

#### Issue: Image Pull Fails

**Symptoms:**
```
Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: TLS handshake timeout
```

**Solution:**
```bash
# Check internet connectivity
ping -c 3 google.com

# Retry with clean state
docker-compose down
docker-compose pull
docker-compose up -d

# Or pull images individually
docker pull eclipse/zenoh:latest
docker pull eclipse/zenoh-bridge-mqtt:latest
docker pull eclipse-mosquitto:latest
```

### Messages Not Flowing

#### Issue: MQTT Messages Not Reaching Zenoh

**Symptoms:**
- MQTT publisher works
- Zenoh subscriber receives nothing

**Diagnosis:**
```bash
# Check MQTT bridge logs
docker-compose logs zenoh-mqtt-bridge | grep -i "error\|warn"

# Verify MQTT bridge is connected to Zenoh
docker-compose logs zenoh-mqtt-bridge | grep -i "connect"

# Test direct MQTT connection to bridge
mosquitto_pub -h localhost -p 1884 -t 'test/debug' -m 'test message' -d
```

**Solution:**
```bash
# Restart the bridge
docker-compose restart zenoh-mqtt-bridge

# Check topic filters in config
cat zenoh-mqtt-bridge/config.json5 | grep -A 5 "allow\|deny"

# Verify scope configuration
# MQTT 'sensor/temp' should appear as 'mqtt/demo/sensor/temp' in Zenoh
```

#### Issue: Zenoh Messages Not Reaching ROS2

**Symptoms:**
- Zenoh router works
- ROS2 topics are empty

**Diagnosis:**
```bash
# Check ROS2 bridge logs
docker-compose logs zenoh-ros2dds-bridge | grep -i "error\|warn"

# List ROS2 topics
docker exec -it ros2-humble ros2 topic list

# Check if bridge is connected
docker-compose logs zenoh-ros2dds-bridge | grep -i "connect"
```

**Solution:**
```bash
# Restart ROS2 bridge
docker-compose restart zenoh-ros2dds-bridge

# Verify ROS2 domain ID matches
docker-compose logs ros2-humble | grep ROS_DOMAIN_ID
docker-compose logs zenoh-ros2dds-bridge | grep ROS_DOMAIN_ID

# Check namespace configuration
cat zenoh-ros2dds-bridge/config.json5 | grep namespace
```

### Performance Issues

#### Issue: High Latency

**Symptoms:**
- Messages delayed by seconds
- Slow response times

**Diagnosis:**
```bash
# Check CPU usage
docker stats

# Check network latency
docker exec zenoh-mqtt-bridge ping -c 10 zenoh-router

# Monitor message rates
docker-compose logs zenoh-router | grep -i "message\|pub\|sub" | tail -n 50
```

**Solution:**
```bash
# Reduce logging level
# Edit docker-compose.yaml:
environment:
  - RUST_LOG=info  # Change from debug to info

# Restart services
docker-compose restart

# Check system resources
free -h
df -h
```

#### Issue: High Memory Usage

**Symptoms:**
- Container using excessive memory
- System becomes slow

**Diagnosis:**
```bash
# Check memory usage per container
docker stats --no-stream

# Check container logs for issues
docker-compose logs zenoh-router | grep -i "memory\|oom"
```

**Solution:**
```bash
# Restart affected service
docker-compose restart zenoh-router

# Add memory limits in docker-compose.yaml:
services:
  zenoh-router:
    mem_limit: 512m
    mem_reservation: 256m

# Clear old logs
docker-compose down
rm -rf mosquitto/log/*
docker-compose up -d
```

### Connection Issues

#### Issue: Can't Access Web Interfaces

**Symptoms:**
- Node-RED not loading at localhost:1880
- REST APIs not responding

**Diagnosis:**
```bash
# Check if service is running
docker ps | grep node-red

# Check port mapping
docker port node-red

# Test port accessibility
curl http://localhost:1880
curl http://localhost:8000
```

**Solution:**
```bash
# Restart the service
docker-compose restart node-red

# Check firewall
sudo ufw status
sudo ufw allow 1880/tcp

# Verify no proxy interfering
curl -v http://localhost:1880
```

#### Issue: External Scripts Can't Connect

**Symptoms:**
- pub.py or sub.py fail to connect
- Connection timeout errors

**Diagnosis:**
```bash
# Test Zenoh router accessibility
nc -zv localhost 7447

# Check if router is listening
docker exec zenoh-router netstat -tuln | grep 7447

# Verify firewall
sudo iptables -L | grep 7447
```

**Solution:**
```bash
# Ensure router is exposing port
docker-compose ps zenoh-router

# Check docker-compose.yaml port mapping:
ports:
  - "7447:7447"  # Must be present

# Restart router
docker-compose restart zenoh-router

# Test connection
telnet localhost 7447
```

### Configuration Issues

#### Issue: Config Changes Not Applied

**Symptoms:**
- Modified configuration has no effect
- Service using old settings

**Solution:**
```bash
# Restart the specific service
docker-compose restart zenoh-mqtt-bridge

# If config is in volume, rebuild
docker-compose down
docker-compose up -d

# For major changes, rebuild image
docker-compose build zenoh-ros2dds-bridge
docker-compose up -d
```

#### Issue: Invalid Configuration

**Symptoms:**
```
Error: Failed to parse config file
```

**Solution:**
```bash
# Validate JSON5 syntax
cat zenoh-mqtt-bridge/config.json5

# Common issues:
# - Missing commas
# - Trailing commas
# - Incorrect quotes
# - Unescaped special characters

# Use online JSON5 validator or:
python3 -c "import json5; json5.load(open('zenoh-mqtt-bridge/config.json5'))"
```

### Data Issues

#### Issue: Malformed Messages

**Symptoms:**
- Subscribers receive garbled data
- JSON parsing errors

**Diagnosis:**
```bash
# Monitor raw messages
docker-compose logs -f zenoh-subscriber

# Check publisher format
mosquitto_pub -h localhost -p 1884 -t 'test' -m '{"test":123}' -d
```

**Solution:**
- Ensure valid JSON format
- Check character encoding (UTF-8)
- Verify message size limits
- Test with simple messages first

## ROS2-Specific Issues

### Issue: ROS2 Topics Not Visible

**Diagnosis:**
```bash
# Enter ROS2 container
docker exec -it ros2-humble bash

# Source ROS2
source /opt/ros/humble/setup.bash

# List topics
ros2 topic list

# Check if bridge is running
ps aux | grep zenoh
```

**Solution:**
```bash
# Verify ROS_DOMAIN_ID
echo $ROS_DOMAIN_ID

# Check DDS configuration
cat /root/cyclonedds.xml

# Restart ROS2 services
docker-compose restart ros2-humble zenoh-ros2dds-bridge
```

### Issue: Foxglove Not Connecting

**Symptoms:**
- Can't connect to ws://localhost:8765
- Blank dashboard

**Solution:**
```bash
# Check if Foxglove bridge is running
docker exec ros2-humble ps aux | grep foxglove

# View Foxglove logs
docker-compose logs ros2-humble | grep foxglove

# Restart ROS2 with Foxglove
docker-compose restart ros2-humble

# Test WebSocket
wscat -c ws://localhost:8765
```

## Debugging Tools

### Enable Debug Logging

```yaml
# In docker-compose.yaml
environment:
  - RUST_LOG=debug  # or trace for maximum verbosity
```

### Interactive Shell Access

```bash
# Access any container
docker exec -it zenoh-router sh
docker exec -it ros2-humble bash
docker exec -it zenoh-mqtt-bridge sh

# Install debugging tools (if needed)
apk add curl netcat-openbsd  # Alpine Linux
apt-get update && apt-get install curl netcat  # Debian/Ubuntu
```

### Network Debugging

```bash
# Capture network traffic
docker exec zenoh-mqtt-bridge tcpdump -i any port 1884

# Test DNS resolution
docker exec zenoh-mqtt-bridge nslookup zenoh-router

# Check routing
docker exec zenoh-mqtt-bridge traceroute zenoh-router
```

## Getting Help

If you can't resolve the issue:

1. **Collect Information:**
   ```bash
   # System info
   docker version
   docker-compose version
   uname -a
   
   # Service logs
   docker-compose logs > logs.txt
   
   # Configuration
   cat docker-compose.yaml
   cat zenoh-mqtt-bridge/config.json5
   cat zenoh-ros2dds-bridge/config.json5
   ```

2. **Search Existing Issues:**
   - [Project Issues](https://github.com/harunkurtdev/zenoh-multi-bridge/issues)
   - [Zenoh Issues](https://github.com/eclipse-zenoh/zenoh/issues)
   - [ROS2 Answers](https://answers.ros.org/)

3. **Create New Issue:**
   - Include system information
   - Attach relevant logs
   - Describe steps to reproduce
   - Mention what you've tried

## Preventive Maintenance

### Regular Checks

```bash
# Weekly: Check disk space
df -h

# Monthly: Update images
docker-compose pull
docker-compose up -d

# Clean old containers/images
docker system prune -a
```

### Monitoring

```bash
# Set up monitoring
docker stats

# Log rotation
# Configure in mosquitto.conf and Docker logging
```

## See Also

- [Installation Guide](getting-started/installation.md)
- [Configuration Guide](configuration/overview.md)
- [Architecture Overview](architecture/overview.md)
