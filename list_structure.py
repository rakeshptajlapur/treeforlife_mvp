import os
from pathlib import Path

def list_files(startpath):
    # Files and directories we're interested in
    important_extensions = {'.py', '.html', '.css', '.js', '.json', '.yml', '.yaml'}
    important_files = {'manage.py', 'requirements.txt', 'Dockerfile', 'docker-compose.yml'}
    
    for root, dirs, files in os.walk(startpath):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules', '.idea', '.vscode']]
        
        # Only process Django-related directories
        if any(name in root for name in ['templates', 'static', 'media', 'migrations']):
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * level
            print(f'{indent}└── {os.path.basename(root)}/')
            
            # Show files in these directories
            subindent = '│   ' * (level + 1)
            for f in files:
                if f.endswith(tuple(important_extensions)) or f in important_files:
                    print(f'{subindent}└── {f}')
        else:
            # For other directories, only show Python files and important files
            if any(f.endswith(tuple(important_extensions)) or f in important_files for f in files):
                level = root.replace(startpath, '').count(os.sep)
                indent = '│   ' * level
                print(f'{indent}└── {os.path.basename(root)}/')
                
                subindent = '│   ' * (level + 1)
                for f in files:
                    if f.endswith(tuple(important_extensions)) or f in important_files:
                        print(f'{subindent}└── {f}')

# Run this from your Django project root directory
current_dir = os.getcwd()
print(f"Django project structure for: {current_dir}\n")
list_files(current_dir)