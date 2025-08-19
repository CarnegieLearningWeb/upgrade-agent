"""
Main entry point for UpGradeAgent.

This is a console-based chatbot for interacting with the UpGrade A/B testing platform.
Users can ask questions, manage experiments, and simulate user interactions through
natural language commands.
"""

import asyncio
import logging
import sys
from typing import Dict, Any

from src.graph import build_upgrade_agent_graph, create_conversation_config, create_initial_state
from src.config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def print_welcome_message():
    """Print welcome message and basic instructions."""
    print("\n" + "="*80)
    print("🚀 Welcome to UpGradeAgent!")
    print("An AI assistant for UpGrade A/B testing platform")
    print("="*80)
    print("\nWhat I can help you with:")
    print("• Explain A/B testing concepts and UpGrade terminology")
    print("• List and search experiments")
    print("• Create, update, and manage experiments")
    print("• Simulate user assignments and decision points")
    print("• Check system health and available contexts")
    print("\nExamples:")
    print('• "What contexts are available?"')
    print('• "Create an experiment called Math Hints"')
    print('• "What conditions did user123 get for the Math experiment?"')
    print('• "Explain what assignment rules are"')
    print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
    print("-"*80 + "\n")


async def handle_user_input(app, config, user_input: str) -> str:
    """
    Process user input through the LangGraph workflow.
    
    Args:
        app: Compiled LangGraph application
        config: Configuration for the conversation
        user_input: User's input message
        
    Returns:
        Bot's response
    """
    try:
        # Use LangGraph's memory to get the current state
        input_data = {"user_input": user_input.strip()}
        
        # Run the workflow (LangGraph handles state persistence automatically)
        result = await app.ainvoke(input_data, config)
        
        # Extract response
        return result.get("final_response", "I apologize, but I couldn't process your request. Please try again.")
        
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        return f"I encountered an error while processing your request: {str(e)}. Please try again."


async def main():
    """Main conversation loop."""
    try:
        # Build the LangGraph workflow
        print("Initializing UpGradeAgent...")
        app = build_upgrade_agent_graph()
        
        # Create conversation configuration
        conversation_id = "console_session"
        config = create_conversation_config(conversation_id)
        
        print_welcome_message()
        
        while True:
            try:
                # Get user input
                user_input = await asyncio.to_thread(input, "You: ")
                user_input = user_input.strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using UpGradeAgent! Goodbye!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                print("Bot: ", end="", flush=True)
                
                # Process the input (LangGraph manages conversation state)
                response = await handle_user_input(app, config, user_input)
                print(response)
                print()  # Add blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in conversation loop: {e}")
                print(f"An unexpected error occurred: {str(e)}")
                print("Please try again.")
                
    except Exception as e:
        logger.error(f"Failed to start UpGradeAgent: {e}")
        print(f"Failed to initialize UpGradeAgent: {str(e)}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    # Verify configuration
    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your Anthropic API key and try again.")
        sys.exit(1)
    
    # Validate all configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Run the main conversation loop
    asyncio.run(main())
