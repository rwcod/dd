# Cline General Instructions

Cline is an AI coding assistant that operates in three modes: **Coder**, **Architect**, and **Ask**. This documentation introduces the Dockerized AI Text-to-Image project, explaining its goal and overall workflow.

---

## 1. Overview

The project aims to implement an AI processing system in a Docker container that:
- Connects to MongoDB to retrieve dataset and model parameters.
- Performs Text-to-Image generation (e.g., using Stable Diffusion).
- Stores generated images in Google Cloud Storage (GCS).
- Logs results in MongoDB.
- Optionally sends a callback notification upon completion.

### Key Components
1. **Docker Container**: Ensures isolated and reproducible environments.
2. **MongoDB**: Provides data retrieval (datasets, AI model configs) and result logging.
3. **AI Model**: Generates images based on textual input.
4. **Google Cloud Storage**: Stores generated images.
5. **Callback URL**: Notifies external systems after processing.

---

## 2. Next Steps

1. **Finalize Model Selection**: Confirm the Text-to-Image framework (e.g., Stable Diffusion, DALL·E, etc.).
2. **Architect**: Outline the high-level design, including Docker setup and data flow.
3. **Coder**: Implement the code, focusing on AI inference, database interaction, and results storage.
4. **Testing & Validation**: Ensure local and containerized testing with integration points (MongoDB, GCS) is successful.
5. **Deployment**: After validation, deploy to a suitable environment (e.g., on-premises server, cloud cluster, etc.).
