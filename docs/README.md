# Documentation

This directory contains the MkDocs documentation for the Zenoh Multi-Protocol Bridge project.

## Building the Documentation

### Prerequisites

- Python 3.8+
- pip

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Building

To build the static documentation site:

```bash
mkdocs build
```

The generated site will be in the `site/` directory.

### Development

To start a local development server with auto-reload:

```bash
mkdocs serve
```

Then open your browser to [http://localhost:8000](http://localhost:8000)

## Documentation Structure

```
docs/
├── index.md                  # Home page
├── getting-started/          # Installation and quick start guides
│   ├── prerequisites.md
│   ├── installation.md
│   └── quick-start.md
├── architecture/             # System architecture documentation
│   ├── overview.md
│   ├── components.md
│   ├── data-flow.md
│   └── network.md
├── components/               # Individual component documentation
│   ├── zenoh-router.md
│   ├── mqtt-broker.md
│   ├── zenoh-mqtt-bridge.md
│   ├── ros2-humble.md
│   ├── zenoh-ros2dds-bridge.md
│   ├── node-red.md
│   └── test-components.md
├── configuration/            # Configuration guides
│   ├── overview.md
│   ├── mqtt-bridge.md
│   ├── ros2-bridge.md
│   └── docker-compose.md
├── usage/                    # Usage guides
│   ├── testing.md
│   ├── multi-protocol.md
│   └── monitoring.md
├── use-cases/                # Real-world use cases
│   ├── iot-robotics.md
│   ├── hybrid-communication.md
│   ├── research.md
│   ├── industrial.md
│   └── smart-city.md
├── api/                      # API reference
│   ├── endpoints.md
│   └── rest-apis.md
├── troubleshooting.md        # Troubleshooting guide
└── contributing.md           # Contributing guidelines
```

## Contributing to Documentation

When contributing to the documentation:

1. **Follow the Existing Structure**: Place new content in the appropriate directory
2. **Use Markdown**: All documentation is in Markdown format
3. **Include Examples**: Code examples and command-line snippets are helpful
4. **Add Diagrams**: Use Mermaid syntax for diagrams when appropriate
5. **Test Your Changes**: Build the docs locally to verify formatting
6. **Update Navigation**: Add new pages to `mkdocs.yml` navigation

### Markdown Features

The documentation supports:

- **Mermaid Diagrams**: For flowcharts and sequence diagrams
- **Code Highlighting**: Syntax highlighting for various languages
- **Admonitions**: Info, warning, and note boxes
- **Tabbed Content**: For platform-specific instructions
- **Task Lists**: For checklists and progress tracking

### Example Admonition

```markdown
!!! warning "Important Note"
    This is a warning message.

!!! info "Information"
    This is an info message.

!!! tip "Pro Tip"
    This is a helpful tip.
```

### Example Tabbed Content

```markdown
=== "Ubuntu"
    ```bash
    sudo apt-get install package
    ```

=== "macOS"
    ```bash
    brew install package
    ```
```

## Deployment

The documentation can be deployed to:

- **GitHub Pages**: `mkdocs gh-deploy`
- **ReadTheDocs**: Connect your repository
- **Static Hosting**: Upload the `site/` directory

## See Also

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
