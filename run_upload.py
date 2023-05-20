import sys
import pandas as pd
from jinja2 import Environment, Template
from pathlib import Path
from helper import upload_and_add_descriptions
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit import print_formatted_text as print

HERE = Path(__file__).parent.resolve()
TEMPLATES = HERE.joinpath("templates").resolve()


def main():
    print("Select the directory with the metadata.csv")
    # Launch Zenity file picker and retrieve the selected file path
    path = subprocess.check_output(
        ["zenity", "--file-selection", "--directory"], text=True
    ).strip()
    path = Path(path)

    # Get user input for Wikipedia credentials
    username = prompt("Enter your Wikimedia Commons username: ")
    password = prompt("Enter your Wikimedia Commons password: ", is_password=True)

    # Load the metadata from the CSV file
    metadata = pd.read_csv(path.joinpath("metadata.csv"))
    # Replace NaNs with empty strings
    metadata = metadata.fillna("")

    # Set up the Jinja2 template
    template = Template(TEMPLATES.joinpath("photograph.jinja2").read_text())

    print("Starting upload of photos in the folder.")
    # Iterate over the metadata and render the template for each row
    for _, row in metadata.iterrows():
        title = row["name"]
        image_path = row["path"]
        description = template.render(row.to_dict())
        upload_and_add_descriptions(
            username,
            password,
            image_path,
            title,
            description,
        )


if __name__ == "__main__":
    main()
