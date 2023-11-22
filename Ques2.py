import json
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime


def load_json(json_file_path):
    """Load JSON data from a file."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def preprocess_and_clean(json_data):

    # Define a function to clean text
    def clean_text(text):
        if text is not None:
            # Remove Unicode escape sequences
            cleaned_text = text.encode('utf-8').decode('unicode-escape')
            # Remove emoji symbols
            cleaned_text = cleaned_text.encode('ascii', 'ignore').decode('ascii')
            # Remove extra whitespaces
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text
        return None
    def convert_to_datetime(date_str):
        if date_str is not None:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        return None

    # Clean and handle null values for top-level attributes
    json_data['CreatedAt'] = convert_to_datetime(json_data.get('CreatedAt'))
    json_data['ClosedAt'] = convert_to_datetime(json_data.get('ClosedAt'))
    json_data['MergedAt'] = convert_to_datetime(json_data.get('MergedAt'))
    json_data['UpdatedAt'] = convert_to_datetime(json_data.get('UpdatedAt'))
    json_data['Title'] = clean_text(json_data.get('Title'))
    json_data['Body'] = clean_text(json_data.get('Body'))

    # Clean and handle null values for nested conversation data
    if 'ChatgptSharing' in json_data:
        for convo in json_data['ChatgptSharing']:
            convo['URL'] = clean_text(convo.get('URL'))
            convo['Title'] = clean_text(convo.get('Title'))
            convo['DateOfConversation'] = convert_to_datetime(convo.get('DateOfConversation'))

            if 'Conversations' in convo:
                convo['Conversations'] = [
                    {
                        'Prompt': clean_text(c.get('Prompt')),
                        'Answer': clean_text(c.get('Answer')),
                        'ListOfCode': c.get('ListOfCode') if 'ListOfCode' in c else None
                    }
                    for c in convo['Conversations']
                ]

    return json_data