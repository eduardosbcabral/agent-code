"""Main Chapter Agent class."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.prompt import Prompt

from config.settings import Config
from config.meta_prompt import META_PROMPT
from core.context import ProjectContextBuilder
from core.gemini_client import GeminiClient
from core.history import ConversationHistory
from core.parser import ThoughtExtractor
from ui.display import display_info, display_error, display_thoughts, display_action, display_observation

console = Console()


class ChapterAgent:
    """The main Chapter Agent class that handles AI interactions and command execution."""
    
    def __init__(self, config: Config, working_directory: Path):
        """Initialize the agent with configuration and working directory."""
        self.config = config
        self.working_directory = working_directory
        self.context_builder = ProjectContextBuilder(working_directory)
        self.gemini_client = GeminiClient(config)
        self.conversation_history = ConversationHistory()
        self.thought_extractor = ThoughtExtractor()
        self.project_context = ""
        
        display_info(f"Agent initialized with workspace: {working_directory}")
    
    async def initialize(self):
        """Initialize the agent components."""
        try:
            # Test Gemini connection
            display_info("Testing Gemini API connection...")
            if not await self.gemini_client.test_connection():
                return False
            
            # Build project context
            display_info("Building project context...")
            self.project_context = await self.context_builder.build_context()
            
            # Initialize conversation with meta-prompt
            meta_prompt_with_context = META_PROMPT.format(project_context=self.project_context)
            self.conversation_history.add_system_message("System initialized", meta_prompt_with_context)
            
            display_info("Agent initialization complete!")
            return True
            
        except Exception as e:
            display_error(f"Failed to initialize agent: {e}")
            return False
    
    async def run(self):
        """Main interaction loop for the agent."""
        # Initialize the agent
        if not await self.initialize():
            display_error("Agent initialization failed. Exiting.")
            return
        
        display_info("Agent is ready! Type your requests below. (Type 'quit' to exit)")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]USER >[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Process the user input
                await self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                display_error(f"Error during interaction: {e}")
    
    async def _process_user_input(self, user_input: str):
        """Process a user input through the AI agent."""
        try:
            # Add user message to history
            self.conversation_history.add_user_message(user_input)
            
            # Get AI response
            display_info("🤔 Agent is thinking...")
            response_data = await self.gemini_client.generate_response(
                self.conversation_history.get_conversation_for_api()
            )
            
            if not response_data:
                display_error("Failed to get response from AI")
                return
            
            # Display thoughts
            if response_data['thoughts']:
                display_thoughts(response_data['thoughts'])
            
            # Extract and parse actions
            parsed_data = self.thought_extractor.extract_thoughts_and_actions(
                response_data['final_text']
            )
            
            # Display and execute actions
            if parsed_data['actions']:
                console.print(f"\n[blue]> Agent is performing {len(parsed_data['actions'])} actions...[/blue]")
                
                observations = []
                for i, action in enumerate(parsed_data['actions'], 1):
                    # Display the action
                    display_action(i, action.get('narration', ''), action['command'])
                    
                    # Execute the action (placeholder for now)
                    observation = await self._execute_action(action)
                    observations.append(f"[Observation for Action {i}]:\n{observation}")
                    
                    # If this is a FINISH action, break
                    if action['type'] == 'FINISH':
                        break
                
                # Display observations
                if observations:
                    display_observation('\n\n'.join(observations))
                    
                    # Add observations to conversation history
                    self.conversation_history.add_observation('\n\n'.join(observations))
            
            # Add assistant response to history
            self.conversation_history.add_assistant_response(
                thoughts=response_data['thoughts'],
                final_text=response_data['final_text'],
                actions=parsed_data['actions']
            )
            
            # Handle final output if FINISH was called
            if parsed_data['has_finish'] and parsed_data['final_output']:
                console.print(f"\n[green]✅ Task Complete![/green]")
                console.print(f"\n[bold]Final Answer:[/bold]\n{parsed_data['final_output']}")
                
        except Exception as e:
            display_error(f"Error processing user input: {e}")
    
    async def _execute_action(self, action: Dict[str, Any]) -> str:
        """Execute a single action and return the observation."""
        try:
            action_type = action['type']
            params = action.get('params', {})
            
            if action_type == 'READ_FILE':
                return f"File reading not implemented yet. Would read: {params.get('file_path')}"
            
            elif action_type == 'WRITE_FILE':
                return f"File writing not implemented yet. Would write to: {params.get('file_path')}"
            
            elif action_type == 'LIST_FILES':
                return "File listing not implemented yet. Would show directory structure."
            
            elif action_type == 'TERMINAL_COMMAND':
                return f"Terminal command not implemented yet. Would execute: {params.get('terminal_command')}"
            
            elif action_type == 'FINISH':
                return "Task marked as complete."
            
            else:
                return f"Unknown action type: {action_type}"
                
        except Exception as e:
            return f"Error executing action: {e}"
