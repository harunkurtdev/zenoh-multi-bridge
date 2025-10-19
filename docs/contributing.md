# Contributing to Zenoh Multi-Protocol Bridge

Thank you for your interest in contributing to the Zenoh Multi-Protocol Bridge project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be Respectful**: Treat everyone with respect and consideration
- **Be Collaborative**: Work together and help each other
- **Be Inclusive**: Welcome and support people of all backgrounds
- **Be Professional**: Maintain professionalism in all interactions

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Git installed
- Docker and Docker Compose
- Basic understanding of the technologies used:
  - Zenoh protocol
  - MQTT
  - ROS2 (for robotics-related contributions)
  - Docker containers

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/zenoh-multi-bridge.git
   cd zenoh-multi-bridge
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/harunkurtdev/zenoh-multi-bridge.git
   ```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

1. **Clear Title**: Descriptive summary of the issue
2. **Description**: Detailed explanation of the problem
3. **Steps to Reproduce**:
   ```
   1. Start services with 'docker-compose up'
   2. Run command X
   3. Observe error Y
   ```
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Environment**:
   - OS: (e.g., Ubuntu 22.04)
   - Docker version: (e.g., 24.0.5)
   - Docker Compose version: (e.g., 2.20.2)
7. **Logs**: Relevant log output
   ```bash
   docker-compose logs [service-name]
   ```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. **Use Case**: Why is this enhancement needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches you've considered
4. **Additional Context**: Screenshots, diagrams, etc.

### Contributing Code

Types of contributions we welcome:

- **Bug fixes**: Corrections to existing functionality
- **New features**: Additional capabilities
- **Performance improvements**: Optimizations
- **Documentation**: Improvements to docs
- **Examples**: New use case examples
- **Tests**: Additional test coverage

## Development Setup

### 1. Local Environment

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/zenoh-multi-bridge.git
cd zenoh-multi-bridge

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Build and Test

```bash
# Build custom images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests (if available)
./run-tests.sh  # Add this if you create test scripts
```

### 3. Make Changes

- Modify code or configuration files
- Test your changes locally
- Ensure all services still work together

### 4. Test Your Changes

```bash
# Restart affected services
docker-compose restart [service-name]

# Test end-to-end
python3 pub.py  # Terminal 1
python3 sub.py  # Terminal 2

# Check logs for errors
docker-compose logs | grep -i error
```

## Coding Standards

### Configuration Files

- Use **JSON5** format for Zenoh configurations
- Include comments explaining non-obvious settings
- Follow existing file structure

Example:
```json5
{
  // Client mode connects to existing router
  mode: "client",
  
  // Connection endpoint
  connect: {
    endpoints: ["tcp/zenoh-router:7447"],
  },
  
  // Plugin configuration
  plugins: {
    mqtt: {
      // MQTT server port
      port: "0.0.0.0:1884",
      // Scope prefix for topics
      scope: "mqtt/demo",
    }
  }
}
```

### Docker Compose

- Keep service definitions organized
- Use meaningful container names
- Document non-standard ports
- Include restart policies

```yaml
services:
  service-name:
    container_name: service-name
    image: image:tag
    restart: unless-stopped
    ports:
      - "host:container"  # Document purpose
    environment:
      - VAR_NAME=value
    networks:
      - zenoh-mqtt-net
```

### Documentation

- Use Markdown format
- Include code examples
- Add diagrams where helpful (Mermaid syntax)
- Keep documentation up-to-date with code changes

## Testing Guidelines

### Manual Testing

1. **Start All Services**
   ```bash
   docker-compose up -d
   docker-compose ps  # Verify all running
   ```

2. **Test MQTT Flow**
   ```bash
   # Terminal 1: Subscribe
   mosquitto_sub -h localhost -p 1883 -t 'test/#' -v
   
   # Terminal 2: Publish
   mosquitto_pub -h localhost -p 1884 -t 'test/msg' -m 'Hello'
   ```

3. **Test Zenoh Flow**
   ```bash
   # Terminal 1: Subscribe
   python3 sub.py
   
   # Terminal 2: Publish
   python3 pub.py
   ```

4. **Test Multi-Protocol**
   - Publish to MQTT
   - Verify in Zenoh subscriber
   - Check ROS2 topics (if applicable)

### Integration Tests

If adding test scripts:

```bash
#!/bin/bash
# test-integration.sh

set -e

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Testing MQTT to Zenoh bridge..."
# Add test commands

echo "All tests passed!"
```

### Performance Testing

For performance-critical changes:

```bash
# Measure message throughput
docker-compose logs zenoh-router | grep -c "published"

# Check latency
# Use timestamps in messages to measure end-to-end latency
```

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for custom MQTT topic filters

- Implement configurable allow/deny patterns
- Update configuration documentation
- Add examples in README

Fixes #123
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (if needed)
- Reference related issues

### Pull Request Process

1. **Update Documentation**
   - Update README if needed
   - Add/update relevant docs in `docs/`
   - Update CHANGELOG if present

2. **Test Your Changes**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   # Run manual tests
   ```

3. **Create Pull Request**
   - Push to your fork
   - Open PR against `main` branch
   - Fill out PR template (if available)
   - Link related issues

4. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Manual testing completed
   - [ ] All services start successfully
   - [ ] Multi-protocol communication works
   
   ## Checklist
   - [ ] Code follows project style
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   
   ## Related Issues
   Fixes #123
   ```

5. **Review Process**
   - Respond to review comments
   - Make requested changes
   - Update PR as needed

### After PR Acceptance

1. **Sync with Upstream**
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   git push origin main
   ```

2. **Delete Feature Branch**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

## Documentation

### Documentation Structure

```
docs/
├── index.md              # Home page
├── getting-started/      # Installation, quick start
├── architecture/         # System design
├── components/           # Component details
├── configuration/        # Configuration guides
├── usage/                # Usage examples
├── use-cases/            # Real-world applications
├── api/                  # API reference
└── troubleshooting.md    # Problem solving
```

### Writing Documentation

- Use clear, concise language
- Include practical examples
- Add diagrams for complex concepts
- Test all code examples
- Keep it updated with changes

### Building Documentation

```bash
# Install dependencies
pip install -r requirements.txt

# Build documentation
mkdocs build

# Serve locally
mkdocs serve

# View at http://localhost:8000
```

## Style Guide

### Markdown

- Use ATX-style headers (`#` not `===`)
- Include blank lines around code blocks
- Use fenced code blocks with language tags
- Keep lines under 120 characters when possible

### Code Examples

```bash
# Good: Include comments and context
# Start the MQTT publisher
mosquitto_pub -h localhost -p 1884 -t 'sensor/temp' -m '{"value":25}'

# Bad: No context or explanation
mosquitto_pub -h localhost -p 1884 -t 'sensor/temp' -m '{"value":25}'
```

## Communication

### Channels

- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code contributions
- **Discussions**: General questions, ideas

### Getting Help

If you need help:

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Open a new issue with "question" label

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS file (if created)
- Mentioned in release notes
- Credited in commit history

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Apache License 2.0).

## Questions?

If you have questions about contributing:

1. Check this guide first
2. Look at existing PRs for examples
3. Open an issue with the "question" label
4. We're here to help!

Thank you for contributing to Zenoh Multi-Protocol Bridge! 🎉
