# Cline General Instructions

Cline is an AI coding assistant that operates in three modes: **Coder**, **Architect**, and **Ask**. This documentation introduces the Dockerized AI Image-to-Text project, explaining its goal and overall workflow.

---

## 1. Overview

The project aims to implement an AI processing system in a Docker container that:
- Connects to MongoDB to retrieve image references and model parameters
- Performs Image-to-Text generation using BLIP model
- Stores generated captions in MongoDB
- Optionally sends a callback notification upon completion

### Key Components
1. **Docker Container**: Ensures isolated and reproducible environments
2. **MongoDB**: Provides data retrieval (datasets, AI model configs) and result logging
3. **AI Model**: Generates text captions from images
4. **Callback URL**: Notifies external systems after processing

---

## 2. Next Steps

1. **Finalize Model Selection**: Confirm the Image-to-Text model implementation (e.g., BLIP, Show-and-Tell, etc.)
2. **Architect**: Outline the high-level design, including Docker setup and data flow
3. **Coder**: Implement the code, focusing on AI inference, database interaction, and results storage
4. **Testing & Validation**: Ensure local and containerized testing with MongoDB integration is successful
5. **Deployment**: After validation, deploy to a suitable environment (e.g., on-premises server, cloud cluster, etc.)