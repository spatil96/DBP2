import pymongo
import json

# Replace with your MongoDB connection details
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Replace 'your_db' with the name of your database and 'your_collection' with the name of your collection
db = client.DataBase
collection = db.NyArticles
# document_count = collection.count_documents({})
# print(document_count)

# Find the first 100 documents in the collection
documents = collection.find().limit(20)

# Loop through and print the documents
for doc in documents:
    doc_json = json.dumps(doc, default=str)
    print(doc)
    print("\n")

# Close the MongoDB connection
client.close()
