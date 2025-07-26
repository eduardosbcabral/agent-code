# Chapter Agent 🤖

A manually controlled Python AI Agent that operates in a sandboxed environment with transparent command execution and structured terminal UI.

## 🎯 Overview

Chapter Agent is an AI-powered development assistant that can:
- Read and write files within a specified directory
- Maintain project context across conversations
- Execute terminal commands with full transparency
- Provide structured, formatted terminal output

## 🚀 Quick Start

### Option 1: Local Development
```bash
# Clone the repository
git clone <repository-url>
cd chapter-agent

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (see Configuration section)
# Run the agent
python main.py
```

### Option 2: Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd chapter-agent

# Copy environment template and configure
cp .env.example .env
# Edit .env with your API keys

# Run with Docker Compose
docker-compose up chapter-agent

# For development with hot reload
docker-compose --profile dev up chapter-agent-dev
```

## 📋 Development Status

This project is currently in development. See [development-plan.md](development-plan.md) for detailed progress tracking and implementation roadmap.

**Current Phase:** Foundation & Setup
**Progress:** 0/25 core tasks completed

## 🔧 Configuration

### Required API Keys:
- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/)

### Environment Setup:
```bash
# Option 1: Environment variables
export GEMINI_API_KEY="your_gemini_key_here"

# Option 2: .env file (recommended for Docker)
cp .env.example .env
# Edit .env file with your actual API key
```

## 🏗️ Architecture

### Core Components:
- **AI Engine**: Google Gemini API for intelligent responses
- **Command System**: Structured command parsing and execution
- **UI Framework**: Rich terminal interface with formatted output
- **Sandbox**: Secure file operations within specified directory

### Available Commands:
- `READ_FILE(path)` - Read file contents
- `WRITE_FILE(path, content)` - Create/modify files
- `LIST_FILES()` - Show directory structure
- `TERMINAL_COMMAND(command)` - Execute any terminal command in working directory
- `FINISH()` - Complete task and provide final output

## 📁 Project Structure

```
chapter-agent/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker orchestration
├── development-plan.md  # Detailed development roadmap
├── workspace/          # Default working directory for Docker
├── config/             # Configuration and settings
├── core/               # Core agent logic
├── tools/              # Command implementations
├── ui/                 # Terminal interface
└── tests/              # Test suite
```

## 🤝 Contributing

This project follows a structured development approach. Check the [development plan](development-plan.md) for current priorities and how to contribute.

## 📄 License

[Add your license here]

---

*Built with ❤️ using Python, Google Gemini AI, and Rich terminal formatting*