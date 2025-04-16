import os
import json

config_file_path = 'core/config/email_organizer_config.json'
absolute_path = os.path.abspath(config_file_path)

print(f"Attempting to load config from: {absolute_path}")

try:
    with open(absolute_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("JSON loaded successfully:")
        print(json.dumps(data, indent=4))
except FileNotFoundError:
    print(f"Error: Config file not found at {absolute_path}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    with open(absolute_path, 'r', encoding='utf-8') as f:
        print("Raw file content:")
        print(f.read())
except Exception as e:
    print(f"An unexpected error occurred: {e}")