"""Display utilities for Chapter Agent terminal UI."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def display_welcome():
    """Display the welcome message and application info."""
    welcome_text = Text()
    welcome_text.append("Chapter Agent", style="bold cyan")
    welcome_text.append(" 🤖\n\n", style="cyan")
    welcome_text.append("A manually controlled Python AI Agent that operates in a sandboxed environment\n")
    welcome_text.append("with transparent command execution and structured terminal UI.\n\n")
    welcome_text.append("Features:", style="bold")
    welcome_text.append("\n• Read and write files within specified directory")
    welcome_text.append("\n• Execute terminal commands with full transparency")
    welcome_text.append("\n• Maintain project context across conversations")
    welcome_text.append("\n• Provide structured, formatted output")
    
    panel = Panel(
        welcome_text,
        title="🚀 Welcome",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)


def display_error(message: str):
    """Display an error message in a formatted panel."""
    console.print(f"\n[red]❌ Error:[/red] {message}")


def display_success(message: str):
    """Display a success message in a formatted style."""
    console.print(f"\n[green]✓[/green] {message}")


def display_info(message: str):
    """Display an info message in a formatted style."""
    console.print(f"\n[blue]ℹ[/blue] {message}")


def display_thoughts(thoughts: str):
    """Display the agent's thoughts in a formatted panel."""
    panel = Panel(
        thoughts,
        title="🧠 Agent's Thoughts",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(panel)


def display_action(action_num: int, narration: str, command: str):
    """Display an action with narration and command."""
    content = Text()
    if narration:
        content.append("💬 Narration: ", style="bold blue")
        content.append(f"{narration}\n")
    content.append("⚙️  Command:   ", style="bold green")
    content.append(command, style="cyan")
    
    panel = Panel(
        content,
        title=f"Action {action_num}",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)


def display_observation(observations: str):
    """Display system observations in a formatted panel."""
    panel = Panel(
        observations,
        title="📋 System Observation",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(panel)
