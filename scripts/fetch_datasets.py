import urllib.request
import json
import os

def fetch_datasets():
    # url = "http://localhost:8085/onfhir-feast/api/Dataset?includeDatasetStats=false&includePopulationStats=false"
    url = "http://localhost/dt4h/feast/api/Dataset?includeDatasetStats=false&includePopulationStats=false"
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the output file
    output_file_path = os.path.join(script_dir, "..", "output-data", "myFhirServer", "dataset", "catalogue.json")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    try:
        # Make the GET request
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                # Save the formatted JSON to the file
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"Successfully saved to {output_file_path}")
            else:
                print(f"Failed to fetch data. Status code: {response.status}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_datasets()

