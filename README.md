# DD Scripts Repository

This repository contains various automation scripts and tools developed by DD. Each project is contained in its own directory with dedicated documentation.

## Projects

### text2img
A script for converting text to images. This project includes:
- Text to image conversion functionality
- Docker support for containerized deployment
- Detailed documentation in `/docs/text2img/`

For more details, see the [text2img documentation](docs/text2img/design.md).

### img2text
A Docker-based application that generates text captions for images using the BLIP model. Features include:
- MongoDB integration for image reference and caption storage
- BLIP model for high-quality image caption generation
- Optional callback notifications
- GPU acceleration support
- Detailed documentation in `/docs/img2text/`

For more details, see the [img2text documentation](docs/img2text/).

## Repository Structure
```
.
├── docs/                    # Documentation root
│   ├── text2img/           # Text to Image project documentation
│   └── img2text/           # Image to Text project documentation
├── text2img/               # Text to Image project
│   ├── app/               # Application source code
│   ├── Dockerfile        # Docker configuration
│   ├── README.md         # Project-specific readme
│   └── requirements.txt  # Python dependencies
├── img2text/              # Image to Text project
│   ├── Dockerfile        # Docker configuration
│   ├── main.py           # Main application script
│   ├── README.md         # Project-specific readme
│   └── requirements.txt  # Python dependencies
└── .gitattributes        # Git attributes configuration
```

## Adding New Projects
When adding a new project:
1. Create a new directory for the project (e.g., `newproject/`)
2. Create corresponding documentation in `docs/project-name/`
3. Include project-specific README.md in the project directory
4. Update this main README.md to list the new project

## Contributing
Each project has its own documentation and contribution guidelines. Please refer to the project-specific documentation in the `/docs` directory.
