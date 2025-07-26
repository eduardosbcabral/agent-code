"""Task completion tool for Agent Code."""

from typing import Dict, Any
from ui.display import display_success


class TaskFinisher:
    """Tool for handling task completion."""
    
    def __init__(self):
        """Initialize the task finisher."""
        pass
        
    async def finish_task(self) -> Dict[str, Any]:
        """Handle the FINISH command."""
        display_success("Task completed - FINISH command received")
        return {
            "success": True,
            "output": "Task completed successfully",
            "finished": True
        }
