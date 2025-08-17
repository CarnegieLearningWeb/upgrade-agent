#!/usr/bin/env python3

import sys
from src.config import config

def main():
    """
UpGradeAgent - Educational AI Assistant for A/B Testing Platform

A conversational AI agent that helps users learn, explore, and work with 
the UpGrade A/B testing platform through natural language interactions.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.graph.builder import create_graph
from src.graph.state import create_initial_state
from src.tools import set_global_state
from src.exceptions.exceptions import UpGradeError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UpGradeAgent:
    """Main UpGradeAgent interface."""
    
    def __init__(self, session_id: str = "default"):
        """Initialize the agent with a session ID."""
        self.session_id = session_id
        self.graph = None
        self.state = None
        
    async def initialize(self) -> None:
        """Initialize the agent graph and state."""
        try:
            # Create initial state
            self.state = create_initial_state("")
            
            # Set global state for tools
            set_global_state(self.state)
            
            # Create the graph
            self.graph = create_graph()
            
            logger.info("UpGradeAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UpGradeAgent: {e}")
            raise UpGradeError(f"Initialization failed: {e}")
    
    async def chat(self, message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: User's input message
            
        Returns:
            Agent's response string
        """
        if not self.graph or not self.state:
            raise UpGradeError("Agent not initialized. Call initialize() first.")
        
        try:
            # Update state with new user message
            self.state["user_input"] = message
            self.state["conversation_history"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run the graph
            config = {"configurable": {"thread_id": self.session_id}}
            result = await self.graph.ainvoke(self.state, config)
            
            # Extract final response
            response = result.get("final_response", "Sorry, I couldn't process your request.")
            
            # Update conversation history with agent response
            self.state["conversation_history"].append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_msg = "I encountered an error processing your request. Please try again."
            return error_msg
    
    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        if not self.state:
            return []
        return self.state.get("conversation_history", [])
    
    def reset_conversation(self) -> None:
        """Reset the conversation state."""
        if self.state:
            self.state["conversation_history"] = []
            self.state["user_input"] = ""
            self.state["final_response"] = None
            logger.info("Conversation reset")


async def main():
    """Main interactive loop for testing the agent."""
    print("🚀 UpGradeAgent - Educational AI Assistant")
    print("Type 'quit' to exit, 'reset' to clear conversation, 'help' for commands\n")
    
    # Initialize agent
    agent = UpGradeAgent()
    
    try:
        await agent.initialize()
        print("✅ Agent initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = await asyncio.to_thread(input, "You: ")
            user_input = user_input.strip()
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                print("🔄 Conversation reset!\n")
                continue
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'history':
                history = agent.get_conversation_history()
                print_history(history)
                continue
            
            # Process message
            print("🤔 Thinking...")
            response = await agent.chat(user_input)
            print(f"Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def print_help():
    """Print available commands."""
    print("\n📖 Available Commands:")
    print("  quit     - Exit the agent")
    print("  reset    - Clear conversation history")
    print("  history  - Show conversation history")
    print("  help     - Show this help message")
    print("\n💬 You can ask about:")
    print("  - UpGrade platform features and concepts")
    print("  - How to create and manage experiments")
    print("  - A/B testing best practices")
    print("  - Platform API usage and integration")
    print("  - Troubleshooting and debugging")
    print() 


def print_history(history: list):
    """Print conversation history."""
    if not history:
        print("📝 No conversation history yet.\n")
        return
    
    print("\n📝 Conversation History:")
    for i, msg in enumerate(history, 1):
        role = "👤 You" if msg["role"] == "user" else "🤖 Agent"
        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        print(f"  {i}. {role}: {content}")
    print() 


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")