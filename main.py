#!/usr/bin/env python3
"""
Chapter Agent - A manually controlled Python AI Agent

Main entry point for the application.
"""

import asyncio
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from config.settings import load_config, Config
from core.agent import ChapterAgent
from ui.display import display_welcome, display_error


console = Console()


def _print_main_formatted(text: str, config: Config = None):
    """Print text with or without formatting based on config."""
    if config and config.debug_raw_content:
        # Strip Rich markup and print plain text
        import re
        plain_text = re.sub(r'\[/?[^\]]*\]', '', text)
        print(plain_text)
    else:
        console.print(text)


def is_running_in_docker():
    """Check if we're running inside a Docker container."""
    return os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER') == 'true'


def get_workspace_suggestions():
    """Get workspace path suggestions based on environment."""
    if is_running_in_docker():
        return [
            "/host/home/{username}/projects/my-project",
            "/host/Users/{username}/Projects/my-project",  # macOS
            "/host/c/Users/{username}/projects/my-project",  # Windows
            "/app/workspace"  # Internal testing
        ]
    else:
        return [
            "/home/{username}/projects/my-project",
            "/Users/{username}/Projects/my-project",  # macOS
            "C:/Users/{username}/projects/my-project",  # Windows
            "./workspace"  # Local testing
        ]


async def main():
    """Main application entry point."""
    config = None  # Initialize config variable
    try:
        # Display welcome message
        display_welcome()
        
        # Load configuration and validate API keys
        config = load_config()
        if not config.validate():
            display_error("Configuration validation failed. Please check your API keys.")
            return
        
        # Prompt for working directory
        suggestions = get_workspace_suggestions()
        
        if is_running_in_docker():
            if config.debug_raw_content:
                print("\nℹ Running in Docker Container")
                print("• External projects: Use /host/ prefix for projects on your host machine")
                print("• Internal workspace: Use /app/workspace for testing")
            else:
                console.print("\n[blue]ℹ Running in Docker Container[/blue]")
                console.print("• [cyan]External projects:[/cyan] Use /host/ prefix for projects on your host machine")
                console.print("• [cyan]Internal workspace:[/cyan] Use /app/workspace for testing")
        else:
            if config.debug_raw_content:
                print("\nℹ Running Locally")
                print("• Any project: Use absolute or relative paths")
            else:
                console.print("\n[blue]ℹ Running Locally[/blue]")
                console.print("• [cyan]Any project:[/cyan] Use absolute or relative paths")
        
        if config.debug_raw_content:
            print("\nExample paths:")
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            console.print("\n[yellow]Example paths:[/yellow]")
            for suggestion in suggestions:
                console.print(f"  {suggestion}")
        
        while True:
            working_dir = Prompt.ask(
                "\n[bold cyan]Enter the full path to your project's working directory[/bold cyan]"
            )
            
            if not working_dir:
                display_error("Working directory path cannot be empty.")
                continue
                
            working_path = Path(working_dir).expanduser().resolve()
            
            if not working_path.exists():
                display_error(f"Directory does not exist: {working_path}")
                continue
                
            if not working_path.is_dir():
                display_error(f"Path is not a directory: {working_path}")
                continue
                
            break
        
        if config.debug_raw_content:
            print(f"\n✓ Agent Initialized. Workspace set to: {working_path}")
        else:
            console.print(f"\n[green]✓[/green] Agent Initialized. Workspace set to: [bold]{working_path}[/bold]")
        
        # Initialize the agent
        agent = ChapterAgent(config, working_path)
        
        # Start the main interaction loop
        await agent.run()
        
    except KeyboardInterrupt:
        if config and config.debug_raw_content:
            print("\n👋 Goodbye!")
        else:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        display_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
