import os
import re

# Define common secret patterns
SECRET_PATTERNS = [
    r'(?i)api[_-]?key\s*=\s*[\'"][A-Za-z0-9]+[\'"]',
    r'(?i)password\s*=\s*[\'"][A-Za-z0-9]+[\'"]',
    r'(?i)secret[_-]?key\s*=\s*[\'"][A-Za-z0-9]+[\'"]',
    r'(?i)token\s*=\s*[\'"][A-Za-z0-9]+[\'"]',
]


def remove_secrets_from_file(file_path):
    """Removes secrets from a Python file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        for pattern in SECRET_PATTERNS:
            line = re.sub(pattern, 'REMOVED_SECRET', line)
        cleaned_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(cleaned_lines)


def process_directory(directory="."):
    """Scans and removes secrets from all Python files in the current directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Cleaning {file_path}...")
                remove_secrets_from_file(file_path)


if __name__ == "__main__":
    process_directory()
    print("Secrets removed successfully!")
