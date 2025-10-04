import os
import json
from kivy.app import App

# Base directory for JSON storage
try:
    # Use this in APK
    BASE_DIR = App.get_running_app().user_data_dir
except Exception:
    # Termux/testing fallback
    BASE_DIR = os.path.join(os.path.dirname(__file__), "user_data")

# Ensure the folder exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_file_path(filename):
    """Get the full path for a JSON file in user_data"""
    return os.path.join(BASE_DIR, filename)

def load_json(filename, default=None):
    """Load JSON data from a file, return default if missing"""
    path = get_file_path(filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(filename, data):
    """Save JSON data to a file"""
    path = get_file_path(filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)