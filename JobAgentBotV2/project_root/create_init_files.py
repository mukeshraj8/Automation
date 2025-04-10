import os

def create_init_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories like .git, .venv, etc.
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue

        init_file = os.path.join(dirpath, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass  # Create an empty __init__.py
            print(f"✅ Created: {init_file}")

if __name__ == "__main__":
    project_root = os.path.dirname(__file__)  # Current directory where script is
    create_init_files(project_root)
