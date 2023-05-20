import os
from PIL import Image
import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import yaml
from pathlib import Path
import subprocess


HERE = Path(__file__).parent.resolve()
TEMPLATES = HERE.joinpath("templates").resolve()


def get_exif_data(file):
    img = Image.open(file)
    if hasattr(img, "_getexif"):
        exif_info = img._getexif()
        if exif_info is not None:
            for tag, value in exif_info.items():
                if tag == 36867:  # Corresponds to DateTimeOriginal in EXIF data
                    return value
    return None


def get_user_input(prompt_message, default_value):
    user_input = input(f"{prompt_message} (Default: {default_value}): ")
    if user_input == "":
        return default_value
    return user_input


def get_path_input(prompt_message, default_value):
    message = f"{prompt_message} (Default: {default_value}): "
    user_input = prompt(message, completer=PathCompleter())
    if user_input == "":
        return default_value
    return user_input


def generate_csv_xls(config):
    csv_header = [
        "path",
        "name",
        "photographer",
        "title",
        "description",
        "depicted_people",
        "depicted_place",
        "date",
        "medium",
        "dimensions",
        "institution",
        "department",
        "references",
        "object_history",
        "exhibition_history",
        "credit_line",
        "inscriptions",
        "notes",
        "accession_number",
        "source",
        "permission",
        "other_versions",
        "license",
        "partnership",
        "categories",
    ]

    data_list = []
    counter = 1
    for subdir, dirs, files in os.walk(config["directory_path"]):
        for file in files:
            if file.endswith(".jpg"):
                path = os.path.join(subdir, file)
                date = get_exif_data(path)
                title = f"{config['title']} - {counter}"
                new_file_name = f"{title}.jpg"
                data = {
                    "path": path,
                    "name": new_file_name,
                    "photographer": f'[[User:{config["user_name"]}]]',
                    "title": title,
                    "description": config["description"],
                    "date": date,
                    "source": "{{own}}",
                    "license": "{{cc-by-4.0}}",
                    "categories": config["category"],
                }
                data_list.append(data)
                counter += 1

    df = pd.DataFrame(data_list, columns=csv_header)

    # Saving to CSV
    df.to_csv(os.path.join(config["directory_path"], "metadata.csv"), index=False)


def load_config(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print("Select the directory with the images:")
    config["directory_path"] = subprocess.check_output(
        ["zenity", "--file-selection", "--directory"], text=True
    ).strip()

    config["title"] = get_user_input("Please enter a title", config.get("title", ""))
    config["description"] = get_user_input(
        "Please enter a description", config.get("description", "")
    )
    config["user_name"] = get_user_input(
        "Please enter a Wikipedia user name of the photographer",
        config.get("user_name", ""),
    )
    config["category"] = get_user_input(
        "Please enter the Commons categories. For multiple categories, separate them with ';'.",
        config.get("category", "Wikimedia Hackathon Athens 2023"),
    )
    return config


if __name__ == "__main__":
    config_path = "./config.yaml"
    config = load_config(config_path)
    generate_csv_xls(config)
