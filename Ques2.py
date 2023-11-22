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