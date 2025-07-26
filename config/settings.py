"""Configuration management for Chapter Agent."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file if it exists
load_dotenv()

console = Console()


@dataclass
class Config:
    """Configuration class for Chapter Agent."""
    
    gemini_api_key: Optional[str] = None
    debug_raw_content: bool = False
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.debug_raw_content = os.getenv("DEBUG_RAW_CONTENT", "false").lower() in ("true", "1", "yes", "on")
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        missing = []
        
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        
        if missing:
            console.print("[red]Missing required environment variables:[/red]")
            for var in missing:
                console.print(f"  - {var}")
            console.print("\n[yellow]Please set these variables in your environment or create a .env file.[/yellow]")
            return False
        
        return True


def load_config() -> Config:
    """Load and return the application configuration."""
    return Config()
