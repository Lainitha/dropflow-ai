import json
import csv
from pathlib import Path

def ensure_directory_exists(directory: str):
    Path(directory).mkdir(parents=True, exist_ok=True)

def read_json(file_path: str):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(data: dict, file_path: str):
    ensure_directory_exists(Path(file_path).parent)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def write_csv(data: list, file_path: str):
    ensure_directory_exists(Path(file_path).parent)
    if data:
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)