# Agent Code

A manually controlled Python AI Agent that operates in a sandboxed environment with transparent command execution and structured terminal UI.

<img width="1203" height="800" alt="Agent Code Demo" src="https://github.com/user-attachments/assets/6620d219-be2b-4552-95c4-0bfe4f042866" />

## Overview

Agent Code is an interactive AI development assistant powered by Google's Gemini AI. It provides a controlled environment where AI can execute commands to read files, write files, list directory structures, and run terminal commands while maintaining full transparency and user oversight.

## Key Features

- 🤖 **AI-Powered Development Assistant** - Leverage Google Gemini AI for intelligent code analysis and generation
- 🔍 **Transparent Command Execution** - Every AI action is clearly displayed and logged
- 📁 **File System Operations** - Read, write, and organize files within specified directories
- 💻 **Terminal Command Execution** - Run shell commands, package managers, and build tools
- 🎨 **Rich Terminal UI** - Beautiful formatted output with panels, colors, and structured display
- 🐳 **Docker Support** - Run in containerized environments for safety and portability
- 🔧 **Debug Mode** - Raw text output option for integration and logging
- 🛡️ **Safety Controls** - Sandboxed execution with path validation and command limits

## Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/))
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent-code
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the agent**
   ```bash
   python main.py
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up agent-code

# For development with hot reload
docker-compose --profile dev up agent-code-dev
```

## Usage

1. **Start the agent** and specify your project directory
2. **Interact naturally** with the AI using plain English
3. **Monitor command execution** in real-time
4. **Review results** and continue the conversation

### Example Interactions

```
"Fix the syntax errors in calculator.py and add unit tests"
"Create a responsive contact form for the website"
"Analyze the sales data and generate a summary report"
"Set up a Python virtual environment and install dependencies"
```

## Project Structure

```
agent-code/
├── config/           # Configuration and AI prompts
│   ├── meta_prompt.py    # AI system instructions
│   └── settings.py       # Application configuration
├── core/             # Core agent functionality
│   ├── agent.py          # Main agent orchestration
│   ├── command_parser.py # AI response parsing
│   ├── command_executor.py # Command execution
│   └── gemini_client.py  # AI client interface
├── tools/            # Available agent tools
│   ├── file_reader.py    # File operations
│   ├── file_writer.py    # File creation/editing
│   └── terminal_executor.py # Shell command execution
├── ui/               # User interface components
│   └── display.py        # Terminal UI formatting
├── workspace/        # Test workspace with sample projects
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Enable raw text output (no formatting)
DEBUG_RAW_CONTENT=false
```

### AI Command Format

The agent uses a structured command format for reliable parsing:

**New Format (Recommended):**
```
<narration>Creating an HTML file</narration>

<code 1><!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body><h1>Hello World</h1></body>
</html></code 1>

<command>[CMD:WRITE_FILE("index.html", "<code 1>")]</command>
```

**Available Commands:**
- `[CMD:LIST_FILES]` - List directory contents
- `[CMD:READ_FILE("path")]` - Read file contents
- `[CMD:WRITE_FILE("path", "<code ID>")]` - Write file using code block
- `[CMD:TERMINAL_COMMAND("command")]` - Execute shell command
- `[CMD:FINISH]` - Complete task and provide final answer

## Test Workspace

The `workspace/` directory contains sample projects for testing:

- **🐍 Python Examples** - Calculator, data analyzer, file processor with intentional bugs
- **🌐 Web Project** - HTML/CSS/JS website with incomplete features
- **📊 Data Analysis** - Sales data cleaning and analysis scripts
- **🔧 Utility Scripts** - File organization and system information tools

### Example Test Scenarios

```bash
# Point the agent to the workspace directory and try:
"Fix the syntax errors in workspace/python-examples/calculator.py"
"Complete the contact form in workspace/web-project/index.html"
"Clean and analyze the data in workspace/data-analysis/sales_data.csv"
"Create unit tests for the calculator functions"
```

## API Reference

### Core Classes

- **`AgentCode`** - Main agent orchestrator
- **`CommandParser`** - Parses AI responses into structured commands
- **`CommandExecutor`** - Executes parsed commands safely
- **`GeminiClient`** - Interfaces with Google Gemini AI

### Safety Features

- **Path Validation** - Prevents directory traversal attacks
- **Command Limits** - Maximum iterations and command counts
- **Sandboxed Execution** - Isolated from system-critical areas
- **Error Recovery** - Graceful handling of failures

## Development

### Running Tests

```bash
# Test command parsing
python -c "from core.command_parser import CommandParser; print('Parser OK')"

# Test AI client connection
python -c "from core.gemini_client import GeminiClient; print('Client OK')"
```

### Debug Mode

Enable raw text output for debugging or integration:

```bash
DEBUG_RAW_CONTENT=true python main.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Notes

- **🔒 API Keys**: Store securely in `.env` files, never commit to version control
- **🛡️ Sandboxing**: Agent operates only within specified directories
- **👥 User Oversight**: All commands are displayed before execution
- **🚫 Limitations**: Cannot access system files or network resources outside workspace

## Troubleshooting

### Common Issues

**API Key Issues:**
- Verify your Gemini API key is valid
- Check the `.env` file is in the correct location
- Ensure no quotes around the API key value

**Permission Errors:**
- Check file/directory permissions
- Ensure the workspace directory is writable
- Run with appropriate user permissions

**Command Parsing Errors:**
- Check AI responses follow the expected format
- Enable debug mode for raw output analysis
- Review meta_prompt.py for instruction updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for powerful language model capabilities
- Rich library for beautiful terminal UI
- The open-source community for inspiration and tools

---

**Ready to start building with AI assistance? Run the agent and let's code together!** 🚀
