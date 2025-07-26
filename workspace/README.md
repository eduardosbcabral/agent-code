# Workspace Directory

This directory is used as the default working directory for the Chapter Agent when running in Docker.

When the agent prompts for a working directory, you can use `/app/workspace` if running in Docker, which will map to this directory on your host system.

## Usage

1. Place any test files or projects you want to work with in this directory
2. When running the agent in Docker, it will have access to these files
3. Any files created by the agent will appear here on your host system

## Example

```bash
# Run with docker-compose
docker-compose up chapter-agent

# When prompted for working directory, enter:
/app/workspace
```
