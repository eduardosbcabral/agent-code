# Docker Setup Guide

This document explains how to set up and run Chapter Agent using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- API keys for Gemini (see main README for details)

## Quick Start

1. **Clone and Configure**
   ```bash
   git clone <repository-url>
   cd chapter-agent
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **Run the Application**
   ```bash
   docker-compose up chapter-agent
   ```

3. **For Development (with hot reload)**
   ```bash
   docker-compose --profile dev up chapter-agent-dev
   ```

## Docker Services

### `chapter-agent` (Production)
- Optimized for production use
- Uses pre-built image with application code baked in
- Suitable for demo and presentation purposes

### `chapter-agent-dev` (Development)
- Development profile with volume mounting
- Code changes reflected immediately without rebuild
- Useful for active development

## Working Directory

The agent can work with projects anywhere on your host machine when running in Docker.

### Path Mapping
- **Host machine root** is mounted at `/host` inside the container
- **Internal workspace** at `/app/workspace` for testing

### Examples

When the agent prompts for a working directory:

**Linux/macOS:**
```
/host/home/username/my-project
/host/Users/username/Projects/my-project
```

**Windows:**
```
/host/c/Users/username/projects/my-project
```

**Internal testing:**
```
/app/workspace
```

### Security Note
The container has read/write access to your entire host filesystem through the `/host` mount. Only run this container in trusted environments and be careful with the projects you specify.

## Volume Mounts

- `./workspace:/app/workspace` - Internal workspace for testing
- `/:/host` - Your entire host machine (for external project access)
- `.:/app` - Full application code (dev profile only)

## Environment Variables

The Docker setup uses these environment variables from your `.env` file:
- `GEMINI_API_KEY` - Your Google Gemini AI API key

## Docker Commands

### Build Image Manually
```bash
docker build -t chapter-agent .
```

### Run Container Manually
```bash
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/workspace:/app/workspace \
  chapter-agent
```

### View Logs
```bash
docker-compose logs chapter-agent
```

### Stop Services
```bash
docker-compose down
```

### Clean Up
```bash
# Remove containers and networks
docker-compose down

# Remove images
docker rmi chapter-agent

# Remove volumes (careful - this deletes workspace data)
docker-compose down -v
```

## Troubleshooting

### Permission Issues
If you encounter permission issues with files in the workspace:
```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER workspace/

# Or run with proper user mapping
docker-compose run --user $(id -u):$(id -g) chapter-agent
```

### API Key Issues
- Ensure your `.env` file has the correct API keys
- Check that the `.env` file is in the same directory as `docker-compose.yml`
- Verify API keys are not quoted in the `.env` file

### Container Won't Start
- Check Docker logs: `docker-compose logs chapter-agent`
- Ensure all required dependencies are in `requirements.txt`
- Verify the Dockerfile builds successfully

## Security Notes

- The container runs as a non-root user (`appuser`) for security
- Only the workspace directory is mounted, limiting file system access
- Environment variables are passed securely through the `.env` file
- The `.env` file is excluded from the Docker build context via `.dockerignore`
