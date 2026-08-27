import urllib.request
import json
import math
import os

# The Dataset endpoint returns at most this many entries per page
PAGE_SIZE = 20

def fetch_page(base_url, page):
    url = f"{base_url}&page={page}"
    print(f"Fetching page {page}: {url}")
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise RuntimeError(f"Failed to fetch data. Status code: {response.status}")
        return json.loads(response.read().decode('utf-8'))

def fetch_datasets():
    # base_url = "http://localhost:8085/onfhir-feast/api/Dataset?includeDatasetStats=false&includePopulationStats=false"
    base_url = "http://localhost/dt4h/feast/api/Dataset?includeDatasetStats=false&includePopulationStats=false"
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the output file
    output_file_path = os.path.join(script_dir, "..", "output-data", "myFhirServer", "dataset", "catalogue.json")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    try:
        # Fetch the first page to learn the total number of entries
        first_page = fetch_page(base_url, 1)
        total = first_page.get("total", 0)
        entries = list(first_page.get("entries") or [])

        # e.g. total=40 -> 2 pages, total=65 -> 4 pages
        total_pages = math.ceil(total / PAGE_SIZE)

        # Fetch the remaining pages
        for page in range(2, total_pages + 1):
            page_data = fetch_page(base_url, page)
            entries.extend(page_data.get("entries") or [])

        # Merge everything into a single payload, keeping any extra top-level fields
        data = dict(first_page)
        data["total"] = total
        data["entries"] = entries

        # Save the formatted JSON to the file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved {len(entries)} of {total} entries to {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_datasets()
