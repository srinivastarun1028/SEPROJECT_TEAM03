import json
import matplotlib.pyplot as plt

class DataProcessor:
    def __init__(self, issues_data, discussions_data):
        self.issues_data = issues_data
        self.discussions_data = discussions_data

    def extract_issues_and_discussions(self):
        resolved_issues = sum(1 for issue in self.issues_data['Sources'] if issue['State'] == 'CLOSED')
        unresolved_issues = len(self.issues_data['Sources']) - resolved_issues

        resolved_discussions = sum(1 for discussion in self.discussions_data['Sources'] if discussion.get('Closed', False))
        unresolved_discussions = len(self.discussions_data['Sources']) - resolved_discussions

        return resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions

    def calculate_success_percentage(self, data, issue_type='issue'):
        total_items = len(data['Sources'])
        
        if issue_type == 'issue':
            resolved_items = sum(1 for item in data['Sources'] if item['State'] == 'CLOSED')
        elif issue_type == 'discussion':
            resolved_items = sum(1 for item in data['Sources'] if item.get('Closed', False))
        else:
            raise ValueError("Invalid issue_type. Use 'issue' or 'discussion'.")

        success_percentage = (resolved_items / total_items) * 100 if total_items > 0 else 0
        return success_percentage

    def clean_data(self):
        # Data cleaning: Filtering out items with Status 404
        self.issues_data['Sources'] = [issue for issue in self.issues_data['Sources'] if issue.get('Status') != 404]
        self.discussions_data['Sources'] = [discussion for discussion in self.discussions_data['Sources'] if
                                            discussion['ChatgptSharing'][0].get('Status') != 404]

    def process_data(self):
        # Data extraction
        resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions = self.extract_issues_and_discussions()

        # Data cleaning and processing
        success_percentage_issues = self.calculate_success_percentage(self.issues_data, issue_type='issue')
        success_percentage_discussions = self.calculate_success_percentage(self.discussions_data, issue_type='discussion')

        return resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
               success_percentage_issues, success_percentage_discussions

class Plotter:
    @staticmethod
    def plot_pie_chart(labels, sizes, title, total, resolved, unresolved, success_percentage):
        colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ff6666']

        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
                                          wedgeprops=dict(width=0.3))

        plt.setp(autotexts, size=8, weight="bold")

        # Display counts and success percentage on the pie chart
        count_str = f"Total: {total}\nResolved: {resolved}\nUnresolved: {unresolved}"
        success_percentage_str = f"Success Percentage: {success_percentage:.2f}%"

        ax.text(0, 0, count_str, horizontalalignment='center', verticalalignment='center',
                fontsize=10, weight='bold', transform=ax.transAxes)
        ax.text(0, -0.3, success_percentage_str, horizontalalignment='center', verticalalignment='center',
                fontsize=10, weight='bold', transform=ax.transAxes)

        ax.axis('equal')
        plt.title(title)
        plt.show()

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
        return None

def main():
    issues_file_path = 'snapshot\\20230831_061759_issue_sharings.json'
    discussions_file_path = 'snapshot\\20230831_061926_discussion_sharings.json'

    issues_data = load_json_file(issues_file_path)
    discussions_data = load_json_file(discussions_file_path)

    if issues_data is not None and discussions_data is not None:
        # Data processing using DataProcessor
        data_processor = DataProcessor(issues_data, discussions_data)
        data_processor.clean_data()  # Clean data
        resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
        success_percentage_issues, success_percentage_discussions = data_processor.process_data()

        # Display results
        print("Issues:")
        print(f"Total Issues: {len(issues_data['Sources'])}")
        print(f"Resolved Issues: {resolved_issues}")
        print(f"Unresolved Issues: {unresolved_issues}")
        print(f"Success Percentage (Issues): {success_percentage_issues:.2f}%")

        # Display pie chart for Issues
        Plotter.plot_pie_chart(
            ['Resolved Issues', 'Unresolved Issues'],
            [resolved_issues, unresolved_issues],
            'Issues',
            len(issues_data['Sources']),
            resolved_issues,
            unresolved_issues,
            success_percentage_issues
        )

        print("\nDiscussions:")
        print(f"Total Discussions: {len(discussions_data['Sources'])}")
        print(f"Resolved Discussions: {resolved_discussions}")
        print(f"Unresolved Discussions: {unresolved_discussions}")
        print(f"Success Percentage (Discussions): {success_percentage_discussions:.2f}%")

        # Display pie chart for Discussions
        Plotter.plot_pie_chart(
            ['Resolved Discussions', 'Unresolved Discussions'],
            [resolved_discussions, unresolved_discussions],
            'Discussions',
            len(discussions_data['Sources']),
            resolved_discussions,
            unresolved_discussions,
            success_percentage_discussions
        )

if __name__ == "__main__":
    main()