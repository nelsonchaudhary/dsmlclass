# config.py
# Central place for constants and settings used across the project

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder where all JSON data files are stored
DATA_DIR = os.path.join(BASE_DIR, "data")

# App-level settings
APP_TITLE = "Courier Management System"