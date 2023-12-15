import json
import matplotlib.pyplot as plt
from collections import defaultdict

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
        resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions = self.extract_issues_and_discussions()

        success_percentage_issues = self.calculate_success_percentage(self.issues_data, issue_type='issue')
        success_percentage_discussions = self.calculate_success_percentage(self.discussions_data, issue_type='discussion')

        # Extract issue types and calculate accuracy for Issues
        issue_types, resolved_issue_types = self.extract_issue_types(self.issues_data)
        accuracy_per_issue_type = self.calculate_issue_type_accuracy(issue_types, resolved_issue_types)

        # Extract resolved and unresolved counts per issue type for Issues
        resolved_issue_counts = defaultdict(int)
        unresolved_issue_counts = defaultdict(int)

        for issue in self.issues_data['Sources']:
            state = issue.get('State', 'OPEN')

            for conversation in issue.get('ChatgptSharing', []):
                for code_block in conversation.get('Conversations', []):
                    prompt = code_block.get('Prompt', '')
                    answer = code_block.get('Answer', '')

                    keywords = ['code', 'bug', 'error', 'feature', 'what is']
                    keyword_counts = defaultdict(int)

                    for keyword in keywords:
                        if keyword in prompt.lower():
                            keyword_counts[keyword] += 1
                        if keyword in answer.lower():
                            keyword_counts[keyword] += 1

                    if keyword_counts:
                        dominant_keyword = max(keyword_counts, key=keyword_counts.get)

                        if state == 'CLOSED':
                            resolved_issue_counts[dominant_keyword] += 1
                        else:
                            unresolved_issue_counts[dominant_keyword] += 1

        print("\nIssues:")
        total_resolved_issues = sum(resolved_issue_counts.values())
        total_unresolved_issues = sum(unresolved_issue_counts.values())

        for issue_type, count in issue_types.items():
            accuracy = accuracy_per_issue_type.get(issue_type, 0)
            print(f"{issue_type.capitalize()}: {count} (Accuracy: {accuracy:.2f}%) "
                  f"Resolved: {resolved_issue_counts[issue_type]}, Unresolved: {unresolved_issue_counts[issue_type]}")

        # Plot pie chart and bar graph for issue types with accuracy for Issues
        self.plot_issue_types_accuracy(issue_types, accuracy_per_issue_type, resolved_issue_counts, unresolved_issue_counts, 'Issue Types')
        self.plot_issue_types_counts(issue_types, resolved_issue_counts, unresolved_issue_counts, 'Issue Types Counts')

        # Extract resolved and unresolved counts for Discussions
        resolved_discussion_counts = sum(1 for discussion in self.discussions_data['Sources'] if discussion.get('Closed', False))
        unresolved_discussion_counts = len(self.discussions_data['Sources']) - resolved_discussion_counts

        print("\nDiscussions:")
        print(f"Resolved Discussions: {resolved_discussion_counts}")
        print(f"Unresolved Discussions: {unresolved_discussion_counts}")

        # Plot pie chart for Discussions
        self.plot_pie_chart(['Resolved Discussions', 'Unresolved Discussions'],
                            [resolved_discussion_counts, unresolved_discussion_counts],
                            'Discussions',
                            len(self.discussions_data['Sources']),
                            resolved_discussion_counts,
                            unresolved_discussion_counts,
                            success_percentage_discussions)

        # Overall accuracy calculations
        overall_accuracy_issues = (total_resolved_issues / (total_resolved_issues + total_unresolved_issues)) * 100 if (total_resolved_issues + total_unresolved_issues) > 0 else 0
        overall_accuracy_discussions = (resolved_discussion_counts / (resolved_discussion_counts + unresolved_discussion_counts)) * 100 if (resolved_discussion_counts + unresolved_discussion_counts) > 0 else 0

        print("\nOverall:")
        print(f"Total Issues: {total_resolved_issues + total_unresolved_issues}")
        print(f"Total Resolved Issues: {total_resolved_issues}")
        print(f"Total Unresolved Issues: {total_unresolved_issues}")
        print(f"Overall Success Percentage (Issues): {overall_accuracy_issues:.2f}%")

        print(f"Total Discussions: {resolved_discussion_counts + unresolved_discussion_counts}")
        print(f"Overall Success Percentage (Discussions): {overall_accuracy_discussions:.2f}%")

        return resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
               success_percentage_issues, success_percentage_discussions

    def extract_issue_types(self, data):
        issue_types = defaultdict(int)
        resolved_issue_types = defaultdict(int)

        for issue in data['Sources']:
            state = issue.get('State', 'OPEN')

            for conversation in issue.get('ChatgptSharing', []):
                for code_block in conversation.get('Conversations', []):
                    prompt = code_block.get('Prompt', '')
                    answer = code_block.get('Answer', '')

                    keywords = ['code', 'bug', 'error', 'feature', 'what is']
                    keyword_counts = defaultdict(int)

                    for keyword in keywords:
                        if keyword in prompt.lower():
                            keyword_counts[keyword] += 1
                        if keyword in answer.lower():
                            keyword_counts[keyword] += 1

                    if keyword_counts:
                        dominant_keyword = max(keyword_counts, key=keyword_counts.get)
                        issue_types[dominant_keyword] += 1

                        if state == 'CLOSED':
                            resolved_issue_types[dominant_keyword] += 1

        return issue_types, resolved_issue_types

    def calculate_issue_type_accuracy(self, issue_types, resolved_issue_types):
        accuracy_per_issue_type = {}

        for issue_type, total_count in issue_types.items():
            resolved_count = resolved_issue_types.get(issue_type, 0)
            accuracy = (resolved_count / total_count) * 100 if total_count > 0 else 0
            accuracy_per_issue_type[issue_type] = accuracy

        return accuracy_per_issue_type

    def plot_issue_types_accuracy(self, issue_types, accuracy_per_issue_type, resolved_issue_counts, unresolved_issue_counts, title):
        labels = list(issue_types.keys())
        sizes = [accuracy_per_issue_type[label] for label in labels]
        colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ff6666', '#c2c2f0']  # Added a new color for the bar graph

        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
                                          wedgeprops=dict(width=0.3))

        plt.setp(autotexts, size=8, weight="bold")

        # Display counts, accuracy, and success percentage on the pie chart
        count_str = ""
        accuracy_str = ""

        for label in labels:
            count_str += f"{label.capitalize()}: {resolved_issue_counts[label]} (Resolved), {unresolved_issue_counts[label]} (Unresolved)\n"
            accuracy_str += f"{label.capitalize()}: {accuracy_per_issue_type[label]:.2f}%\n"

        ax.text(0, 0, count_str, horizontalalignment='center', verticalalignment='center',
                fontsize=10, weight='bold', transform=ax.transAxes)
        ax.text(0, -0.3, accuracy_str, horizontalalignment='center', verticalalignment='center',
                fontsize=10, weight='bold', transform=ax.transAxes)

        ax.axis('equal')
        plt.title(title)
        plt.show()

    def plot_issue_types_counts(self, issue_types, resolved_issue_counts, unresolved_issue_counts, title):
        labels = list(issue_types.keys())
        resolved_counts = [resolved_issue_counts[label] for label in labels]
        unresolved_counts = [unresolved_issue_counts[label] for label in labels]
        width = 0.35
        x = range(len(labels))

        fig, ax = plt.subplots()
        ax.bar(x, resolved_counts, width, label='Resolved', color='#66b3ff')
        ax.bar(x, unresolved_counts, width, bottom=resolved_counts, label='Unresolved', color='#ff6666')

        ax.set_xlabel('Issue Types')
        ax.set_ylabel('Counts')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        plt.show()

    def plot_pie_chart(self, labels, sizes, title, total, resolved, unresolved, success_percentage):
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
        data_processor = DataProcessor(issues_data, discussions_data)
        data_processor.clean_data()
        resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
        success_percentage_issues, success_percentage_discussions = data_processor.process_data()

if __name__ == "__main__":
    main()

    
    
    
    
