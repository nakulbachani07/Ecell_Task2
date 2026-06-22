import os
import json


def create_folder(folder_path):
    """
    Creates a folder if it does not already exist.
    """
    os.makedirs(folder_path, exist_ok=True)


def save_json(data, file_path):
    """
    Saves Python data into a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_json(file_path):
    """
    Loads data from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def print_separator():
    """
    Prints a separator line for cleaner terminal output.
    """
    print("-" * 80)


def get_unique_sources(search_results):
    """
    Extracts unique source files and page numbers from search results.
    """
    sources = []
    used_sources = set()

    for result in search_results:
        source_file = result.get("source_file", "unknown")
        page_number = result.get("page_number", "unknown")

        source_key = (source_file, page_number)

        if source_key not in used_sources:
            sources.append({
                "source_file": source_file,
                "page_number": page_number
            })
            used_sources.add(source_key)

    return sources