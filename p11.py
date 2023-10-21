import pymongo
import ast
from datetime import datetime
import matplotlib.pyplot as plt

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["DataBase"]
collection = db["NyArticles"]

# Define the year you want to analyze
#year_to_analyze = 2000

# Counter to limit the number of iterations
max_iterations = 10000000
iteration_count = 0

# Cleanse and insert data into MongoDB
for article in collection.find({}):
    # Limit the number of iterations
    if iteration_count >= max_iterations:
        break

    # Extract the publication year
    pub_date = datetime.strptime(article['pub_date'], '%Y-%m-%d %H:%M:%S+00:00')
    year = pub_date.year

    if year in range(2000,2023):
        # Check if 'keywords' field is empty or malformed
        if 'keywords' in article and article['keywords']:
            try:
                keywords = ast.literal_eval(article['keywords'])
                print(keywords)
                keyword_values = [kw['value'] for kw in keywords]
            except (SyntaxError, ValueError):
                # Handle malformed or empty 'keywords' field
                continue
        else:
            # Handle empty 'keywords' field
            continue

        # Create a document to insert into MongoDB
        document = {
            'year': year,
            'keywords': keyword_values
        }

        # Insert the document into the MongoDB collection
        db["CA"].insert_one(document)

    iteration_count += 1

# Query data for the specified year
# pipeline = [
#     {
#         '$match': {'year': year_to_analyze}
#     },
#     {
#         '$unwind': '$keywords'  # Split the keywords into separate documents
#     },
#     {
#         '$group': {
#             '_id': '$keywords',
#             'count': {'$sum': 1}
#         }
#     },
#     {
#         '$sort': {'count': -1}
#     }
# ]
start_year = 2000
end_year = 2023

# Update the $match stage in the pipeline
pipeline = [
    {
        '$match': {
            'year': {
                '$gte': start_year,
                '$lte': end_year
            }
        }
    },
    {
        '$unwind': '$keywords'  # Split the keywords into separate documents
    },
    {
        '$group': {
            '_id': '$keywords',
            'count': {'$sum': 1}
        }
    },
    {
        '$sort': {'count': -1}
    }
]

result = list(db["CA"].aggregate(pipeline))

# Display the query result and plot it
keywords = [entry['_id'] for entry in result]
counts = [entry['count'] for entry in result]

# Plot the data
plt.figure(figsize=(10, 6))
plt.bar(keywords, counts)
plt.xlabel('Keywords')
plt.ylabel('Count')
plt.title(f'Keyword Frequencies for {year_to_analyze}')
plt.xticks(rotation=90)
plt.show()
