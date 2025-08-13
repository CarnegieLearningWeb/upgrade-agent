#!/usr/bin/env python3

import sys
from src.config import config

def main():
    print("UpGradeAgent v0.1.0")
    print("Type 'quit' or 'exit' to stop the chat")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print(f"You said: {user_input}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            if config.DEBUG:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()