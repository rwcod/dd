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

## Testing the Services

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB of RAM available
- (Optional) NVIDIA GPU with CUDA support

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ddscript
   ```

2. Place test images in `data/images/` directory for img2text service

3. Start the services:
   ```bash
   docker-compose up -d
   ```

### Testing text2img
1. Add text prompts to MongoDB:
   ```bash
   docker-compose exec mongodb mongosh
   use text2img
   db.prompts.insertMany([
     { text: "A beautiful sunset over mountains", status: "pending" },
     { text: "A cute puppy playing in the grass", status: "pending" }
   ])
   ```

2. Check output:
   - Generated images will be in `data/output/` directory
   - Check MongoDB for status updates:
     ```bash
     db.prompts.find({ status: "completed" })
     ```

### Testing img2text
1. Add image references to MongoDB:
   ```bash
   docker-compose exec mongodb mongosh
   use img2text
   db.images.insertMany([
     { path: "/app/images/image1.jpg", status: "pending" },
     { path: "/app/images/image2.jpg", status: "pending" }
   ])
   ```

2. Check results:
   ```bash
   db.images.find({ status: "completed" })
   ```

### Stopping Services
```bash
docker-compose down
```

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
│   ├── app/              # Application source code
│   ├── Dockerfile        # Docker configuration
│   ├── README.md         # Project-specific readme
│   └── requirements.txt  # Python dependencies
├── data/                  # Test data directory
│   ├── images/           # Test images for img2text
│   └── output/           # Generated images from text2img
├── docker-compose.yml     # Docker Compose configuration
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
