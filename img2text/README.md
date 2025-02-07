# DD Scripts Repository

This repository contains various automation scripts and tools developed by DD. Each project is contained in its own directory with dedicated documentation.

## Projects

### text2img
A script for converting text to images. This project includes:
- Text to image conversion functionality
- Docker support for containerized deployment
- Detailed documentation in `/docs/text2img/`

For more details, see the [text2img documentation](docs/text2img/design.md).

## Repository Structure
```
.
├── docs/                    # Documentation root
│   └── text2img/           # Text to Image project documentation
├── text2img/               # Text to Image project
│   ├── app/               # Application source code
│   ├── Dockerfile        # Docker configuration
│   ├── README.md         # Project-specific readme
│   └── requirements.txt  # Python dependencies
└── .gitattributes        # Git attributes configuration
```

## Adding New Projects
When adding a new project:
1. Create a new directory for the project (e.g., `img2text/`)
2. Create corresponding documentation in `docs/project-name/`
3. Include project-specific README.md in the project directory
4. Update this main README.md to list the new project

## Contributing
Each project has its own documentation and contribution guidelines. Please refer to the project-specific documentation in the `/docs` directory.
