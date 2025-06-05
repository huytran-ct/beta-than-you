import re
from typing import List


def process_json_format(text: str) -> str:
    text = text.replace("\n*", "\n *")
    text = text.replace("\n\n", "\n")
    text = re.sub(r'[ \t]+', ' ', text.strip())
    text = text.rstrip("\n")
    text = text.replace('''json\n''', '').replace('''```''', '').replace("'", '"')
    return text

def extract_gcs_path(gcs_path: str) -> str:
    pattern = r"gs://[^/]+/(.+)"
    match = re.search(pattern, gcs_path)
    extracted_subpath = ""
    if match:
        extracted_subpath = match.group(1)
    else:
        print("No match found.")
    return extracted_subpath

def convert_gcs_uri_to_http_path(gcs_uri: str, http_domain: str) -> str:
    new_path = extract_gcs_path(gcs_uri)
    return f"{http_domain}/{new_path}"

def convert_list_gcs_uri_to_http_paths(gcs_uri_list: List[str], http_domain: str) -> List[str]:
    return [convert_gcs_uri_to_http_path(uri, http_domain) for uri in gcs_uri_list]

def convert_text_file_to_list_of_string(file_path: str) -> str:
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Remove any leading/trailing whitespace characters from each line
    items = [line.strip() for line in lines]
    # Join the items with ", " as the separator
    result = ", ".join(items)
    return result

