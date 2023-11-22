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