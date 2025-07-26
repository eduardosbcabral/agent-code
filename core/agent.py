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
from core.command_executor import CommandExecutor
from core.command_parser import CommandParser
from ui.display import display_info, display_error, display_thoughts, display_action, display_observation, display_warning

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
        self.command_executor = CommandExecutor(str(working_directory))
        self.command_parser = CommandParser()
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
        """Process a user input through the AI agent with continuous task execution."""
        try:
            # Add user message to history
            self.conversation_history.add_user_message(user_input)
            
            # Start task execution loop - continues until FINISH command or max iterations
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            task_completed = False
            total_commands = 0
            max_commands = 20
            
            while not task_completed and iteration < max_iterations and total_commands < max_commands:
                iteration += 1
                
                # Get AI response
                display_info("🤔 Agent is thinking...")
                response_data = await self.gemini_client.generate_response(
                    self.conversation_history.get_conversation_for_api(),
                )
                
                if not response_data:
                    display_error("Failed to get response from AI. Trying simplified approach...")
                    # Try with a simpler prompt to recover
                    simple_prompt = f"Continue working on: {user_input}. What should be the next step?"
                    self.conversation_history.add_user_message(simple_prompt)
                    response_data = await self.gemini_client.generate_response(
                        self.conversation_history.get_conversation_for_api(),
                    )
                    if not response_data:
                        display_error("Unable to get AI response after retry. Ending task.")
                        break
                
                # Display thoughts
                if response_data['thoughts']:
                    display_thoughts(response_data['thoughts'])
                
                # Parse the response for commands
                parsed_response = self.command_parser.parse_response(response_data['final_text'])
                
                # Validate commands
                validation = self.command_parser.validate_commands(parsed_response['commands'])
                if not validation['valid']:
                    display_error("Invalid commands detected in AI response")
                    for error in validation['errors']:
                        display_error(f"  - {error}")
                    break
                
                # Check if AI response has commands
                if not parsed_response['commands']:
                    # No commands - AI might be providing final answer
                    if parsed_response['final_output']:
                        console.print(f"\n[green]✅ Task Complete![/green]")
                        console.print(f"\n[bold]Final Answer:[/bold]\n{parsed_response['final_output']}")
                        task_completed = True
                    else:
                        # No commands and no final output - add response and continue
                        self.conversation_history.add_assistant_response(
                            thoughts=response_data['thoughts'],
                            final_text=response_data['final_text'],
                            actions=[]
                        )
                    break
                
                # Display command summary
                console.print(f"\n[blue]{self.command_parser.format_command_summary(parsed_response['commands'])}[/blue]")
                
                # Check command limit
                command_count = len(parsed_response['commands'])
                total_commands += command_count
                
                if total_commands > max_commands:
                    display_error(f"Command limit exceeded: {total_commands} (limit: {max_commands})")
                    display_error("Task execution stopped to prevent runaway operations")
                    break
                
                # Display narrations if present
                for i, narration in enumerate(parsed_response['narrations']):
                    console.print(f"\n[dim]Agent: {narration}[/dim]")
                
                # Execute commands
                observations = []
                
                for i, command in enumerate(parsed_response['commands']):
                    display_action(i + 1, "", f"[CMD:{command['type']}]")
                    
                    # Execute the command
                    result = await self.command_executor.execute_command(
                        command['type'], 
                        command['args']
                    )
                    
                    if result['success']:
                        # Format observation based on command type for better readability
                        if command['type'] == 'READ_FILE':
                            # For file content, format with proper line breaks and code block
                            file_content = result['output']
                            observation = f"[Command {i+1} - {command['type']}]: Successfully read file '{command['args'][0]}'\n\nFile Content:\n```\n{file_content}\n```"
                        elif command['type'] == 'LIST_FILES':
                            observation = f"[Command {i+1} - {command['type']}]: {result['output']}"
                        elif command['type'] == 'WRITE_FILE':
                            observation = f"[Command {i+1} - {command['type']}]: Successfully wrote {result.get('size', 0)} characters to '{command['args'][0]}'"
                        elif command['type'] == 'TERMINAL_COMMAND':
                            observation = f"[Command {i+1} - {command['type']}]: Executed '{command['args'][0]}'\n\nOutput:\n{result['output']}"
                        else:
                            observation = f"[Command {i+1} - {command['type']}]: {result['output']}"
                    else:
                        observation = f"[Command {i+1} - {command['type']} ERROR]: {result.get('error', 'Unknown error')}"
                        display_error(f"Command failed: {result.get('error', 'Unknown error')}")
                    
                    observations.append(observation)
                    
                    # Check for FINISH command - this terminates the operation
                    if command['type'] == 'FINISH':
                        task_completed = True
                        console.print(f"\n[green]🏁 FINISH command received - Task completion signaled[/green]")
                        break
                
                # Display observations
                if observations:
                    display_observation('\n\n'.join(observations))
                    
                    # Add observations to conversation history
                    self.conversation_history.add_observation('\n\n'.join(observations))
                
                # Add assistant response to history (for this iteration)
                self.conversation_history.add_assistant_response(
                    thoughts=response_data['thoughts'],
                    final_text=response_data['final_text'],
                    actions=[]
                )
                
                # Handle final output when task is completed
                if task_completed:
                    if parsed_response['final_output']:
                        console.print(f"\n[green]✅ Task Complete![/green]")
                        console.print(f"\n[bold]Final Answer:[/bold]\n{parsed_response['final_output']}")
                    else:
                        console.print(f"\n[green]✅ Task Complete![/green]")
                        console.print(f"\n[bold]Final Answer:[/bold] Operation completed successfully.")
                    break
                
                # Continue loop for next AI iteration (unless FINISH was called)
            
            # Handle cases where loop ended without proper completion
            if not task_completed and total_commands > 0:
                if iteration >= max_iterations:
                    display_warning(f"Task execution stopped after {max_iterations} iterations")
                elif total_commands >= max_commands:
                    display_warning(f"Task execution stopped after {total_commands} commands (limit: {max_commands})")
                else:
                    display_warning(f"{total_commands} commands executed without FINISH command")
                display_warning("The AI should end operations with a FINISH command.")
                
        except Exception as e:
            display_error(f"Error processing user input: {e}")