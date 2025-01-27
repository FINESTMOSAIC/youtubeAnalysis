import sys
import json
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download vader_lexicon if not already downloaded
nltk.download('vader_lexicon', quiet=True)
analyzer = SentimentIntensityAnalyzer()

def classify_comment(comment):
    # Get the sentiment score
    sentiment = analyzer.polarity_scores(comment)
    
    # Classify the comment based on the score
    if sentiment['compound'] > 0:
        return 'Agree'
    elif sentiment['compound'] < 0:
        return 'Disagree'
    else:
        return 'Neutral'

def extract_month(timestamp):
    try:
        # Parse the timestamp and extract the month
        date = datetime.fromisoformat(timestamp)
        return date.strftime("%B")  # Returns full month name
    except ValueError:
        return "Unknown"


def process_comments(comments):
    global agree_count, disagree_count, neutral_count
    monthly_summary = {}
    total_monthly_comments = {}

    for comment in comments:
        # If the comment is a string, process it directly
        if isinstance(comment, str):
            sentiment = classify_comment(comment)
            month = "Unknown"  # No timestamp for a plain string comment
        else:
            # Assuming comment is a dictionary
            sentiment = classify_comment(comment.get("text", ""))
            month = extract_month(comment.get("timestamp", ""))

        # Update sentiment counts
        if sentiment == 'Agree':
            agree_count += 1
        elif sentiment == 'Disagree':
            disagree_count += 1
        else:
            neutral_count += 1

        # Update monthly sentiment counts
        if month not in monthly_summary:
            monthly_summary[month] = {"Agree": 0, "Disagree": 0, "Neutral": 0}
        monthly_summary[month][sentiment] += 1

        # Update total monthly comment count
        if month not in total_monthly_comments:
            total_monthly_comments[month] = 0
        total_monthly_comments[month] += 1

    return {
        "overall": {
            "agree_count": agree_count,
            "disagree_count": disagree_count,
            "neutral_count": neutral_count,
        },
        "monthly_summary": monthly_summary,
        "total_comments_monthly": total_monthly_comments,
    }

agree_count = 0
disagree_count = 0
neutral_count = 0

if __name__ == "__main__":
    # Read input from stdin
    comments = json.loads(sys.stdin.read())  # Read and parse the JSON input
    sentiment = process_comments(comments)
    print(json.dumps(sentiment, indent=4))  # Output the sentiment results with indentation
