from flask import Flask, request, jsonify
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download vader_lexicon if not already downloaded
nltk.download('vader_lexicon', quiet=True)
analyzer = SentimentIntensityAnalyzer()

app = Flask(__name__)

# Global counters
agree_count = 0
disagree_count = 0
neutral_count = 0

def classify_comment(comment):
    """
    Get the sentiment score and classify the comment as Agree, Disagree, or Neutral.
    """
    sentiment = analyzer.polarity_scores(comment)
    
    if sentiment['compound'] > 0:
        return 'Agree'
    elif sentiment['compound'] < 0:
        return 'Disagree'
    else:
        return 'Neutral'

def extract_month(timestamp):
    """
    Parse the timestamp and extract the month. If parsing fails, return "Unknown".
    """
    try:
        date = datetime.fromisoformat(timestamp)
        return date.strftime("%B")
    except ValueError:
        return "Unknown"

def process_comments(comments):
    """
    Process comments to classify their sentiment and summarize them by month.
    """
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

@app.route('/analyze', methods=['POST'])
def analyze_comments():
    """
    API endpoint to analyze a list of comments.
    """
    global agree_count, disagree_count, neutral_count
    agree_count = 0
    disagree_count = 0
    neutral_count = 0

    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"error": "Invalid input. Expected a list of comments."}), 400

        # Process comments
        sentiment = process_comments(data)
        return jsonify(sentiment)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
