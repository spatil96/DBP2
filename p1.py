import pymongo

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["DataBase"]
collection = db["NyArticles"]

# Define the year you want to analyze
year_to_analyze = 2000

# Query data for the specified year
pipeline = [
    {
        "$match": {"year": year_to_analyze}
    },
    {
        "$unwind": "$keywords"
    },
    {
        "$group": {
            "_id": "$keywords",
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"count": -1}
    }
]

result = list(collection.aggregate(pipeline))
print(result)
# Print the top keywords for the specified year
for item in result:
    print(f"Keyword: {item['_id']}, Frequency: {item['count']}")
