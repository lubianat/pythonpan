import requests
import pandas as pd
from pathlib import Path
from login import BHL_API_KEY
from tqdm import tqdm

API_KEY = BHL_API_KEY
ITEM_ID = "103761"

def get_item_metadata(item_id):
    """
    Fetch metadata (including page-level details) for a specific BHL item.
    """
    base_url = f"""https://www.biodiversitylibrary.org/api3?op=GetItemMetadata&id={item_id}&pages=true&format=json&apikey={API_KEY}"""
    print(base_url)
    response = requests.get(base_url)
    data = response.json()
    if data["Status"] == "ok":
        return data["Result"]
    else:
        print(f"Error: {data.get('ErrorMessage', 'Unknown error')}")
        return None


def download_images_from_bhl(item_metadata, title_metadata, download_directory="bhl_images"):
    """
    Download illustration pages from a BHL item. Store relevant metadata
    (e.g., local file paths, page IDs, item volume/year) into a CSV.
    """

    # Convert download_directory to a Path and ensure it exists
    download_directory = Path(download_directory)
    download_directory.mkdir(parents=True, exist_ok=True)
    item_metadata = item_metadata[0]
    pages = item_metadata.get("Pages", [])
    short_title_name = title_metadata[0].get("ShortTitle", "")
    # If short title is large, get only the starting words
    if len(short_title_name.split()) > 5:
        stub_title = " ".join(short_title_name.split()[:5])
    else:
        stub_title = short_title_name
    item_id = item_metadata["ItemID"]
    volume = item_metadata.get("Volume", "")
    year   = item_metadata.get("Year", "")
    title_id = item_metadata.get("TitleID", "")
    
    records = []  # For CSV rows

    for page in tqdm(pages):
        page_id = page.get("PageID")
        img_url = page.get("FullSizeImageUrl", None)
        page_numbers = ", ".join(
                f"{pn.get('Prefix', '')} {pn.get('Number', '')}".strip()
                for pn in page.get("PageNumbers", [])
            )
        if not img_url:
            continue

        # If you only want illustration pages
        page_types = page.get("PageTypes", [])
        illustration_types = {
            "Illustration", "Plate", "Figure", "Chart", "Map", "Photograph"
        }
        is_illustration = any(
            pt.get("PageTypeName", "").strip() in illustration_types for pt in page_types
        )

        if not is_illustration:
            continue

        # Construct a local filepath using Path
        # Construct filename like A monograph of Odontoglossum (Plate 22) BHL12870361.jpg
        if len(short_title_name.split()) > 5:
            filename = f"{stub_title}... ({page_numbers}) BHL{page_id}.jpg"
        else:
            filename = f"{short_title_name} ({page_numbers}) BHL{page_id}.jpg"
        filepath = download_directory / filename
        
        # Skip download if it already exists
        if filepath.exists():
            print(f"Skipping {filename} (already exists)")
        else:
            print(f"Downloading {img_url} -> {filepath}")
            resp = requests.get(img_url)
            with open(filepath, "wb") as f:
                f.write(resp.content)

        # Create a metadata record for this page
        record = {
            "local_path": str(filepath),
            "filename": filename,
            "short_title": short_title_name,
            "page_id": page_id,
            "item_id": item_id,
            "title_id": title_id,
            "volume": volume,
            "year": year,
            "page_url": page.get("PageUrl", ""),
            "page_numbers": page_numbers,
            "page_types": "; ".join(
                pt.get("PageTypeName", "") for pt in page_types
            ),
            "license": "BHL-no-known-restrictions",  # Adjust as needed
            "categories": ["Files from the Biodiversity Heritage Library", f"{short_title_name}"],
            
        }
        records.append(record)

    # Save all records to a CSV file
    if records:
        csv_path = download_directory / "metadata.csv"
        df = pd.DataFrame(records)
        df.to_csv(csv_path, index=False)
        print(f"\nMetadata saved to {csv_path}")
    else:
        print("No pages were downloaded (no illustrations found, or no pages).")


def get_title_metadata(item_metadata):
    """
    Fetch metadata for the title associated with a BHL item.
    """
    title_id = item_metadata[0].get("TitleID")
    base_url = f"""https://www.biodiversitylibrary.org/api3?op=GetTitleMetadata&id={title_id}&format=json&apikey={API_KEY}"""
    print(base_url)
    response = requests.get(base_url)
    data = response.json()
    if data["Status"] == "ok":
        return data["Result"]
    else:
        print(f"Error: {data.get('ErrorMessage', 'Unknown error')}")
        return None
    
if __name__ == "__main__":
    item_metadata = get_item_metadata(ITEM_ID)
    title_metadata = get_title_metadata(item_metadata)
    if not item_metadata or not title_metadata:
        print("No metadata returned; exiting.")
    else:
        download_images_from_bhl(item_metadata, title_metadata, download_directory="bhl_images")


