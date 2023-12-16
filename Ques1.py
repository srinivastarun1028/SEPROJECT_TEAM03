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

        return dict(issue_types), dict(resolved_issue_types)

    def calculate_issue_type_accuracy(self, issue_types, resolved_issue_types):
        accuracy_per_issue_type = {}

        for issue_type, total_count in issue_types.items():
            resolved_count = resolved_issue_types.get(issue_type, 0)
            accuracy = (resolved_count / total_count) * 100 if total_count > 0 else 0
            accuracy_per_issue_type[issue_type] = accuracy

        return accuracy_per_issue_type

    def plot_issue_types_accuracy(self, issue_types, accuracy_per_issue_type, resolved_issue_counts, unresolved_issue_counts, title):
        labels = list(issue_types.keys())
        counts = list(issue_types.values())
        accuracies = [accuracy_per_issue_type.get(issue_type, 0) for issue_type in labels]

        colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ff6666', '#c2c2f0']
        explode = (0.05, 0.05, 0.05, 0.05, 0.05)  # Adjusted explode for better clarity

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))  # Increased figure size

    # Plot ring chart for issue types with accuracy
        ax1.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.85, explode=explode, wedgeprops=dict(width=0.3))
        ax1.axis('equal')
        ax1.set_facecolor('white')  # Set a white background for better clarity

    # Draw a circle at the center to make it a ring chart
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax1.add_patch(centre_circle)

    # Display additional information on the ring chart
        total_issues = sum(counts)
        total_resolved_issues = sum(resolved_issue_counts.values())
        total_unresolved_issues = sum(unresolved_issue_counts.values())

        count_str = f"Total: {total_issues}\nResolved: {total_resolved_issues}\nUnresolved: {total_unresolved_issues}"
        ax1.text(0, 0, count_str, horizontalalignment='center', verticalalignment='center',
                fontsize=10, weight='bold', transform=ax1.transAxes)

        ax1.set_title(f'{title} Distribution')

    # Customize bar graph for issue types
        bar_width = 0.35
        index = range(len(labels))
        bar1 = ax2.bar(index, [resolved_issue_counts.get(issue_type, 0) for issue_type in labels], bar_width, label='Resolved', color='#66b3ff')
        bar2 = ax2.bar(index, [unresolved_issue_counts.get(issue_type, 0) for issue_type in labels], bar_width, bottom=[resolved_issue_counts.get(issue_type, 0) for issue_type in labels], label='Unresolved', color='#ff6666')

        ax2.set_xticks(index)
        ax2.set_xticklabels(labels)
        ax2.set_ylabel('Counts')
        ax2.set_title(f'Resolved and Unresolved Counts per {title}')
        ax2.legend()

        plt.tight_layout()
        plt.show()



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

        # Extract issue types and calculate accuracy for Discussions
        discussion_types, resolved_discussion_types = self.extract_issue_types(self.discussions_data)
        accuracy_per_discussion_type = self.calculate_issue_type_accuracy(discussion_types, resolved_discussion_types)

        # Extract resolved and unresolved counts per issue type for Discussions
        resolved_discussion_counts = defaultdict(int)
        unresolved_discussion_counts = defaultdict(int)

        for discussion in self.discussions_data['Sources']:
            state = discussion.get('Closed', False)

            for conversation in discussion.get('ChatgptSharing', []):
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

                        if state:
                            resolved_discussion_counts[dominant_keyword] += 1
                        else:
                            unresolved_discussion_counts[dominant_keyword] += 1

        print("\nDiscussions:")
        total_resolved_discussions = sum(resolved_discussion_counts.values())
        total_unresolved_discussions = sum(unresolved_discussion_counts.values())

        for issue_type, count in discussion_types.items():
            accuracy = accuracy_per_discussion_type.get(issue_type, 0)
            print(f"{issue_type.capitalize()}: {count} (Accuracy: {accuracy:.2f}%) "
                  f"Resolved: {resolved_discussion_counts[issue_type]}, Unresolved: {unresolved_discussion_counts[issue_type]}")

        # Plot pie chart and bar graph for issue types with accuracy for Discussions
        self.plot_issue_types_accuracy(discussion_types, accuracy_per_discussion_type, resolved_discussion_counts, unresolved_discussion_counts, 'Discussion Types')

        # Overall accuracy calculations
        overall_accuracy_issues = (total_resolved_issues / (total_resolved_issues + total_unresolved_issues)) * 100 if (total_resolved_issues + total_unresolved_issues) > 0 else 0
        overall_accuracy_discussions = (total_resolved_discussions / (total_resolved_discussions + total_unresolved_discussions)) * 100 if (total_resolved_discussions + total_unresolved_discussions) > 0 else 0

        print("\nOverall:")
        print(f"Total Issues: {total_resolved_issues + total_unresolved_issues}")
        print(f"Total Resolved Issues: {total_resolved_issues}")
        print(f"Total Unresolved Issues: {total_unresolved_issues}")
        print(f"Overall Success Percentage (Issues): {overall_accuracy_issues:.2f}%")

        print(f"Total Discussions: {total_resolved_discussions + total_unresolved_discussions}")
        print(f"Total Resolved Discussions: {total_resolved_discussions}")
        print(f"Total Unresolved Discussions: {total_unresolved_discussions}")
        print(f"Overall Success Percentage (Discussions): {overall_accuracy_discussions:.2f}%")

        return resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
               success_percentage_issues, success_percentage_discussions

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
    issues_file_path = 'snapshot/20230831_061759_issue_sharings.json'
    discussions_file_path = 'snapshot/20230831_061926_discussion_sharings.json'

    issues_data = load_json_file(issues_file_path)
    discussions_data = load_json_file(discussions_file_path)

    if issues_data is not None and discussions_data is not None:
        data_processor = DataProcessor(issues_data, discussions_data)
        data_processor.clean_data()
        resolved_issues, unresolved_issues, resolved_discussions, unresolved_discussions, \
        success_percentage_issues, success_percentage_discussions = data_processor.process_data()

        
if __name__ == "__main__":
    main()
