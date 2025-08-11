#!/usr/bin/env python3
"""
Utility script to compile all documentation files into a single COMPILED_README.md
for easy copy-pasting into Claude/ChatGPT conversations.
"""

import os
from datetime import datetime

def compile_readme():
    """Compile multiple markdown files into a single COMPILED_README.md file."""
    
    # List of files to compile in order
    files_to_compile = [
        'README.md',
        'docs/CORE_TERMS.md', 
        'docs/ASSIGNMENT_BEHAVIOR.md',
        'docs/API_REFERENCE.md',
        'docs/TOOLS.md',
        'docs/GRAPH_STRUCTURE.md',
        'docs/EXAMPLE_CHATS.md'
    ]
    
    # Output file
    output_file = 'COMPILED_README.md'
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from scripts/
    
    with open(os.path.join(script_dir, output_file), 'w', encoding='utf-8') as outfile:
        # Add header with compilation info
        outfile.write(f"# UpGradeAgent - Compiled Documentation\n\n")
        outfile.write(f"*Compiled on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        outfile.write("---\n\n")
        
        for i, filename in enumerate(files_to_compile):
            file_path = os.path.join(script_dir, filename)
            
            if os.path.exists(file_path):
                print(f"Adding {filename}...")
                
                # Add file header
                outfile.write(f"# FILE: {filename}\n\n")
                
                # Read and write file content
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                
                # Add separator
                outfile.write('\n\n---\n\n')
            else:
                print(f"Warning: {filename} not found, skipping...")
    
    print(f"\nCompilation complete! All files merged into {output_file}")
    print(f"File location: {os.path.join(script_dir, output_file)}")

if __name__ == "__main__":
    compile_readme()