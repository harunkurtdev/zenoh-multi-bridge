# Prerequisites

Before setting up the Zenoh Multi-Protocol Bridge, ensure you have the following prerequisites installed on your system.

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB free space
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11 with WSL2

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8 GB or more
- **Storage**: 20 GB free space
- **Network**: Stable internet connection for downloading Docker images

## Required Software

### Docker and Docker Compose

The project is containerized using Docker, so you need Docker and Docker Compose installed.

=== "Ubuntu/Debian"

    ```bash
    # Update package index
    sudo apt-get update
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    
    # Add your user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose
    sudo apt-get install docker-compose-plugin
    
    # Verify installation
    docker --version
    docker compose version
    ```

=== "macOS"

    ```bash
    # Install Docker Desktop for Mac
    # Download from: https://www.docker.com/products/docker-desktop
    
    # Or using Homebrew
    brew install --cask docker
    
    # Verify installation
    docker --version
    docker compose version
    ```

=== "Windows"

    ```powershell
    # Install Docker Desktop for Windows
    # Download from: https://www.docker.com/products/docker-desktop
    
    # Or using Chocolatey
    choco install docker-desktop
    
    # Verify installation (in PowerShell)
    docker --version
    docker compose version
    ```

### Git

Git is required to clone the repository.

=== "Ubuntu/Debian"

    ```bash
    sudo apt-get update
    sudo apt-get install git
    git --version
    ```

=== "macOS"

    ```bash
    # Git comes with Xcode Command Line Tools
    xcode-select --install
    
    # Or using Homebrew
    brew install git
    git --version
    ```

=== "Windows"

    ```powershell
    # Download Git for Windows
    # https://git-scm.com/download/win
    
    # Or using Chocolatey
    choco install git
    git --version
    ```

## Optional Tools

### Python 3 (for test scripts)

Python 3.8+ is required if you want to run the external test scripts (`pub.py` and `sub.py`).

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# macOS
brew install python3

# Windows
# Download from: https://www.python.org/downloads/
```

Install Zenoh Python library:

```bash
pip3 install zenoh
```

### MQTT Clients

For testing MQTT communication, you might want to install MQTT client tools.

```bash
# Ubuntu/Debian
sudo apt-get install mosquitto-clients

# macOS
brew install mosquitto

# Windows
# Download from: https://mosquitto.org/download/
```

### ROS2 (Optional)

If you want to interact with ROS2 topics from your host machine (not required for running the project):

```bash
# Ubuntu 22.04 (Jammy)
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y

# Add ROS2 GPG key
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS2 Humble
sudo apt update
sudo apt install ros-humble-desktop
```

## Network Configuration

### Port Availability

Ensure the following ports are available on your system:

| Port | Service | Protocol |
|------|---------|----------|
| 1880 | Node-RED | HTTP |
| 1883 | Mosquitto MQTT | MQTT |
| 1884 | MQTT Bridge | MQTT |
| 7447 | Zenoh Router | Zenoh/TCP |
| 7449 | ROS2 Bridge | Zenoh/TCP |
| 8000 | Zenoh REST API | HTTP |
| 8001 | MQTT Bridge API | HTTP |
| 8002 | ROS2 Bridge API | HTTP |
| 8765 | Foxglove Bridge | WebSocket |
| 9001 | Mosquitto WebSocket | WebSocket |

Check if ports are in use:

```bash
# Linux/macOS
netstat -tuln | grep -E '1880|1883|1884|7447|7449|8000|8001|8002|8765|9001'

# Or using lsof
lsof -i :1880 -i :1883 -i :1884 -i :7447 -i :7449 -i :8000 -i :8001 -i :8002 -i :8765 -i :9001
```

### Firewall Configuration

If you're running a firewall, you may need to allow traffic on the required ports:

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 1880/tcp
sudo ufw allow 1883/tcp
sudo ufw allow 1884/tcp
sudo ufw allow 7447/tcp
sudo ufw allow 7449/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8765/tcp
sudo ufw allow 9001/tcp
```

## Verification

After installing all prerequisites, verify your setup:

```bash
# Check Docker
docker --version
docker compose version
docker ps

# Check Git
git --version

# Check Python (optional)
python3 --version
pip3 --version

# Check MQTT client (optional)
mosquitto_pub --help
```

## Next Steps

Once you have all prerequisites installed, proceed to the [Installation](installation.md) guide to set up the Zenoh Multi-Protocol Bridge.
