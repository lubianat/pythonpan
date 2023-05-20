import requests


def upload_file_to_commons(file_path, filename, username, password):
    S = requests.Session()

    # Step 1: Retrieve a login token
    login_token = S.get(
        url="https://commons.wikimedia.org/w/api.php",
        params={"action": "query", "meta": "tokens", "type": "login", "format": "json"},
    ).json()["query"]["tokens"]["logintoken"]

    # Step 2: Send a post request to log in
    S.post(
        "https://commons.wikimedia.org/w/api.php",
        data={
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login_token,
            "format": "json",
        },
    )

    # Step 3: Get the CSRF token
    csrf_token = S.get(
        url="https://commons.wikimedia.org/w/api.php",
        params={"action": "query", "meta": "tokens", "format": "json"},
    ).json()["query"]["tokens"]["csrftoken"]

    # Step 4: Upload the file
    with open(file_path, "rb") as file:
        response = S.post(
            "https://commons.wikimedia.org/w/api.php",
            files={"file": file},
            data={
                "action": "upload",
                "filename": filename,
                "token": csrf_token,
                "format": "json",
                "ignorewarnings": 1,  # add this to ignore any warnings
            },
        )

    # check if upload was successful
    if response.json().get("upload", {}).get("result") == "Success":
        print(f"Successfully uploaded {filename}")
        return 1
    else:
        print(f"Could not upload {filename}. Response: {response.json()}")
        return 0


def add_description_to_file_page(filename, description, username, password):
    S = requests.Session()

    # Login same as before
    login_token = S.get(
        url="https://commons.wikimedia.org/w/api.php",
        params={"action": "query", "meta": "tokens", "type": "login", "format": "json"},
    ).json()["query"]["tokens"]["logintoken"]

    S.post(
        "https://commons.wikimedia.org/w/api.php",
        data={
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login_token,
            "format": "json",
        },
    )

    # Get CSRF token
    csrf_token = S.get(
        url="https://commons.wikimedia.org/w/api.php",
        params={"action": "query", "meta": "tokens", "format": "json"},
    ).json()["query"]["tokens"]["csrftoken"]

    # Send a POST request to edit the page
    edit_response = S.post(
        "https://commons.wikimedia.org/w/api.php",
        data={
            "action": "edit",
            "title": f"File:{filename}",
            "token": csrf_token,
            "format": "json",
            "text": description,
            "summary": "adding description",
        },
    )

    # check if editing was successful
    if edit_response.json().get("edit", {}).get("result") == "Success":
        print(f"Successfully added description to {filename}")
    else:
        print(
            f"Could not add description to {filename}. Response: {edit_response.json()}"
        )


def upload_and_add_descriptions(username, password, path, commons_name, description):
    if upload_file_to_commons(path, commons_name, username, password):
        add_description_to_file_page(commons_name, description, username, password)
