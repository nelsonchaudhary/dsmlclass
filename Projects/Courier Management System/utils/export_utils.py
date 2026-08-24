# utils/export_utils.py
# Generic CSV export utility — converts any list of dictionaries into a CSV file.

import csv
import os
import logging
from datetime import datetime


def export_to_csv(records, filename_prefix, export_folder="exports"):
    """
    Writes a list of dictionaries to a CSV file.
    records: list of dicts, e.g. [{"customer_id": 1, "name": "Ram"}, ...]
    filename_prefix: e.g. "customers" -> produces "customers_2026-08-22.csv"
    Returns the full path of the created file, or None if it failed.
    """
    if not records:
        print("No records to export.")
        return None

    # Make sure the exports folder exists
    os.makedirs(export_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    file_path = os.path.join(export_folder, filename)

    try:
        # Use the keys of the first record as the column headers
        fieldnames = list(records[0].keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        return file_path

    except Exception as e:
        logging.error(f"CSV export failed for {filename_prefix}: {e}")
        print(f"Error exporting {filename_prefix}: {e}")
        return None