import re
import argparse
import json

def extract_file_info_from_json(file_id):
    json_file = 'google_drive_files.json'
    try:
        with open(json_file, 'r', encoding='utf-8') as json_data:
            data = json.load(json_data)
            if file_id in data:
                return data[file_id]
            else:
                return None
    except Exception as e:
        print(f'Error: {e}')
        return None

def extract_file_id_from_google_drive_link(link):
    try:
        # Define a regular expression pattern to match Google Drive file IDs
        pattern = r'(?:https?://)?(?:www\.)?(?:drive\.google\.com|docs\.google\.com)/[^\s/]+/d/([a-zA-Z0-9_-]+)'

        # Search for the pattern in the link
        match = re.search(pattern, link)

        if match:
            # Extract and return the file ID
            file_id = match.group(1)
            return file_id
        else:
            return None
    except Exception as e:
        print(f'Error: {e}')
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract file name from Google Drive link')
    parser.add_argument('link', type=str, help='Google Drive link')

    args = parser.parse_args()
    file_id = extract_file_id_from_google_drive_link(args.link)

    if file_id:
        file_info = extract_file_info_from_json(file_id)

        if file_info:
                print(f'File ID: {file_id}')
                print(f'File Name: {file_info["File Name"]}')
                print(f'File Path: {file_info["File Path"]}')
                print(f'MIME Type: {file_info["MIME Type"]}')
        else:
                print(f'File ID {file_id} not found in the JSON file.')
    else:
        print('File ID not found in the link.')

if __name__ == '__main__':
    main()
