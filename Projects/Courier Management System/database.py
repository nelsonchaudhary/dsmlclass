# database.py
# Handles reading and writing JSON data files safely.
# Acts as our "database layer" since we're using JSON instead of SQL.

import json
import os
import logging
from config import DATA_DIR

# Configure logging so errors get recorded, not just printed
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data(filename):
    """
    Reads a JSON file from the data folder and returns its content
    as a Python dictionary. If the file is missing or corrupted,
    handles the error gracefully instead of crashing the app.
    """
    file_path = os.path.join(DATA_DIR, filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        print(f"Error: {filename} not found. Creating a new one.")
        return {}

    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {file_path}")
        print(f"Error: {filename} is corrupted or badly formatted.")
        return {}


def save_data(filename, data):
    """
    Writes a Python dictionary to a JSON file in the data folder.
    Returns True if successful, False if something went wrong.
    """
    file_path = os.path.join(DATA_DIR, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True

    except Exception as e:
        logging.error(f"Failed to save {filename}: {e}")
        print(f"Error: Could not save data to {filename}.")
        return False

