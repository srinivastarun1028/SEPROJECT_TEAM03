import json
import matplotlib.pyplot as plt

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError as e:
        print(f"Error: File not found at path {e.filename}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in the file {file_path}")
        return None
    
    class DataProcessor:
    def _init_(self, issues_data, discussions_data):
        self.issues_data = issues_data
        self.discussions_data = discussions_data

    def extract_issues_and_discussions(self):
        resolved_issues = sum(1 for issue in self.issues_data['Sources'] if issue['State'] == 'CLOSED')
        unresolved_issues = len(self.issues_data['Sources']) - resolved_issues

        resolved_discussions = sum(1 for discussion in self.discussions_data['Sources'] if discussion.get('Closed', False))
        unresolved_discussions = len(self.discussions_data['Sources']) - resolved_discussions

        return resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions