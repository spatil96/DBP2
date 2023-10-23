import pymongo
import re

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["DataBase"]
collection = db["NyArticles"]

# Query the database to retrieve the reader comments
comments = collection.find({"document_type": "comment"})  # Adjust the query as needed

# Initialize a dictionary to store adjectives and their frequencies
adjective_freq = {}

# Define a function to extract adjectives from text
def extract_adjectives(text):
    # Use regular expressions to find adjectives (you may need to adjust the pattern)
    adjectives = re.findall(r'\b\w+JJ\b', text, re.IGNORECASE)
    return adjectives

# Extract adjectives from comments and count their frequencies
for comment in comments:
    text = comment.get("comment_text", "")  # Adjust the field name as needed
    if text:
        adjectives = extract_adjectives(text)
        for adj in adjectives:
            adj = adj.lower()  # Convert to lowercase for consistency
            adjective_freq[adj] = adjective_freq.get(adj, 0) + 1

# Sort the adjectives by frequency (most used first)
sorted_adjectives = sorted(adjective_freq.items(), key=lambda x: x[1], reverse=True)

# Extract the top N adjectives (you can adjust the number as needed)
top_adjectives = [adj for adj, freq in sorted_adjectives[:10]]

# Define a sentiment analysis function (you can use your own method)
def analyze_sentiment(text, adjectives):
    # Implement your sentiment analysis logic here using the extracted adjectives
    # You can use the adjectives to influence sentiment analysis

    # This is a simplified example where sentiment is positive if any of the top adjectives is present
    for adj in adjectives:
        if adj in text:
            return "positive"

    # If none of the top adjectives are found, sentiment is neutral
    return "neutral"

# Initialize variables to store sentiment analysis results
positive_comments = []
neutral_comments = []

# Analyze the sentiment of comments based on the top adjectives
for comment in comments:
    text = comment.get("comment_text", "")  # Adjust the field name as needed
    if text:
        sentiment = analyze_sentiment(text, top_adjectives)
        if sentiment == "positive":
            positive_comments.append(text)
        else:
            neutral_comments.append(text)

# Calculate the number of comments in each category
num_positive_comments = len(positive_comments)
num_neutral_comments = len(neutral_comments)

# Print the results
print(f"Positive Comments: {num_positive_comments}")
print(f"Neutral Comments: {num_neutral_comments}")
