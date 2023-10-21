import pymongo
import matplotlib.pyplot as plt
from datetime import datetime
from bson.code import Code

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["DataBase"]
collection = db["NyArticles"]

# Define the date range
start_year = 2000
end_year = 2023

# Cleanse and insert data into MongoDB in bulk
pipeline = [
    {
        '$match': {
            '$and': [
                {"pub_date": {"$gte": f"{start_year}-01-01"}},
                {"pub_date": {"$lte": f"{end_year}-12-31"}}
            ]
        }
    },
    {
        '$match': {"keywords": {"$exists": True, "$ne": None, "$not": {"$size": 0}}}
    },
    {
        '$addFields': {
            'pub_date': {
                '$dateFromString': {
                    'dateString': '$pub_date',
                    'format': '%Y-%m-%d %H:%M:%S+00:00'
                }
            }
        }
    },
    {
        '$project': {
            'year': {'$year': '$pub_date'},
            'keywords': 1
        }
    }
]

result = list(collection.aggregate(pipeline))
print(result)

# Insert data in bulk
bulk_insert = []
for article in result:
    year = article['year']
    keywords = article['keywords']
    for keyword in keywords:
        bulk_insert.append({
            'year': year,
            'keyword': keyword
        })

if bulk_insert:
    db["CA"].insert_many(bulk_insert)

# # Aggregate keywords for each year and calculate counts
# mapper = Code("""
#     function () {
#         emit({ year: this.year, keyword: this.keyword }, 1);
#     }
# """)
# reducer = Code("""
#     function (key, values) {
#         return Array.sum(values);
#     }
# """)
# finalize = Code("""
#     function (key, reducedVal) {
#         var max = 0;
#         var keyword = "";
#         for (var i in reducedVal) {
#             if (reducedVal[i] > max) {
#                 max = reducedVal[i];
#                 keyword = i;
#             }
#         }
#         return { count: max, keyword: keyword };
#     }
# """)
# result = db["CA"].map_reduce(mapper, reducer, "CA_reduce", finalize=finalize)

# Show max of each year
pipeline = [
    {
        '$group': {
            '_id': "$_id.year",
            'max_keyword': {'$max': "$value.count"}
        }
    },
    {
        '$sort': {'_id': 1}
    }
]

max_counts = list(result.aggregate(pipeline))
for entry in max_counts:
    print(f"Year: {entry['_id']}, Max Keyword: {entry['max_keyword']}")

# Plot keyword frequencies for each year
pipeline = [
    {
        '$group': {
            '_id': {
                'year': '$year',
                'keyword': '$keyword'
            },
            'count': {'$sum': 1}
        }
    },
    {
        '$group': {
            '_id': '$_id.year',
            'keywords': {
                '$push': {
                    'keyword': '$_id.keyword',
                    'count': '$count'
                }
            }
        }
    }
]

result = list(db["CA"].aggregate(pipeline))

for entry in result:
    year = entry['_id']
    keywords_data = entry['keywords']
    keywords = [kw['keyword'] for kw in keywords_data]
    counts = [kw['count'] for kw in keywords_data]

    # Plot the data for each year
    plt.figure(figsize=(10, 6))
    plt.bar(keywords, counts)
    plt.xlabel('Keywords')
    plt.ylabel('Count')
    plt.title(f'Keyword Frequencies for {year}')
    plt.xticks(rotation=90)
    plt.show()
