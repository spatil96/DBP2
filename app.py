from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
import json
import plotly
import plotly.express as px
import os
import ast
from datetime import datetime
from collections import Counter
import plotly.graph_objects as go


project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, 'templates')
app = Flask(__name__, template_folder=template_path)

# Connection to MongoDB
def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)
    return conn[db]

@app.route('/Q2')
def get_data():
    db = "DataBase"
    collection = "monthcomments"
    db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)
    cursor = db[collection].find() 
    result_list = list(cursor)
    
    # Construct a dictionary for JSON response
    result_dict = {
        item["month"]: {"happy": item["happy"], "sad": item["sad"], "neutral": item["neutral"]}
        for item in result_list
    }

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(result_dict, orient='index')

    # Plot the bar graph
    fig = px.bar(df, 
                 x=df.index, 
                 y=["happy", "neutral", "sad"], 
                 barmode='group', 
                 labels={"index": "Month"})

    # Convert the plot to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Q2.html', graphJSON=graphJSON)

@app.route('/Q3')
def get_top_keywords():
    # Your existing code to fetch data from MongoDB
    db = "DataBase"
    collection = "Top_keywords_per_year"
    db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)
    top_keywords_data = list(db[collection].find({}, {'_id': 0}))

    # Create a DataFrame from the MongoDB data
    df = pd.DataFrame(top_keywords_data)

    # Use plotly express to create an interactive histogram
    fig = px.bar(df, x='year', y='counts', color='keyword',
                 labels={'counts': 'Counts'},
                 title='Top Keywords Counts Per Year')
                #  height=500, width=800)

    # Convert the plot to JSON
    graphJSONQ3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the template with the graphJSON data
    return render_template('Q3.html', graphJSONQ31=graphJSONQ3)

@app.route('/')
def get_trend_analysis():
    db = "DataBase"
    collection = "NyArticles"
    db = _connect_mongo(host='localhost', port=27017, username=None, password=None, db=db)

# Define the range of years you want to analyze
    start_year = 2000
    end_year = 2023

    # Counter to limit the number of iterations
    max_iterations = 200000
    iteration_count = 0
        # MongoDB aggregation pipeline

    pipeline = [
        {
            '$match': {'pub_date': {'$gte': f'{start_year}-01-01', '$lt': f'{end_year + 1}-01-01'}}
        },
        {
            '$addFields': {
                'parsed_pub_date': {'$toDate': '$pub_date'}
            }
        },
        {
            '$unwind': '$keywords'
        },
        {
            '$match': {'keywords': {'$ne': None}}
        },
        {
            '$group': {
                '_id': {'year': {'$year': '$parsed_pub_date'}, 'keyword': '$keywords'},
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id.year': 1, '_id.month': 1, 'count': -1}
        },
        {
            '$group': {
                '_id': '$_id.year',
                'top_keyword': {'$first': '$_id.keyword'},
                'top_count': {'$first': '$count'}
            }
        },
        {
            '$sort': {'_id': 1}
        },{
            '$limit': 200 
        }
    ]


        # Retrieve data from MongoDB using the pipeline
    result =  list(db[collection].aggregate(pipeline))
     # Extract data for plotting
    years = [entry['_id'] for entry in result]

    # Create a Plotly figure
    fig = go.Figure()

    for year in years:
        year_data = [entry for entry in result if '_id' in entry and entry['_id'] == year]
        if year_data:
            top_keyword_str = year_data[0]['top_keyword']
            top_keyword_list = ast.literal_eval(top_keyword_str)
            top_keyword_value = top_keyword_list[0]['value']
            top_count = year_data[0]['top_count']

            fig.add_trace(go.Bar(x=[year], y=[top_count], name=top_keyword_value))

    # Update layout
    fig.update_layout(
        xaxis=dict(title='Year'),
        yaxis=dict(title='Counts'),
        title='Top Keywords Counts Per Year',
        barmode='group'
    )


    # Convert the plot to JSON
    graphJSONQ3 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the template with the graphJSON data
    return render_template('Q1.html', graphJSONQ1=graphJSONQ3)

if __name__ == '__main__':

    app.run(debug=True)

#kill $(lsof -t -i:8080) ---------to kill process at 5000

# ---------------------Query 2 as the data is 1.9m we did this---------------------------------------------------------------------------------------------------
# from pymongo import MongoClient
# import matplotlib.pyplot as plt

#
# client = MongoClient('mongodb://localhost:27017')
# db = client['nytimes']
# collection = db['comment months']

#
# positive_words = ['happy', 'great', 'fantastic', 'positive', 'good', 'love']
# negative_words = ['sad', 'bad', 'terrible', 'negative', 'hate', 'worst']

#
# pipeline = [
#     {
#         '$project': {
#             'Date': 1,
#             'commentBody': 1,
#             'sentiment': {
#                 '$cond': {
#                     'if': {'$and': [
#                         {'$eq': [{'$type': '$commentBody'}, 'string']},
#                         {'$regexMatch': {'input': '$commentBody', 'regex': '|'.join(positive_words), 'options': 'i'}}
#                     ]},
#                     'then': 'happy',
#                     'else': {
#                         '$cond': {
#                             'if': {'$and': [
#                                 {'$eq': [{'$type': '$commentBody'}, 'string']},
#                                 {'$regexMatch': {'input': '$commentBody', 'regex': '|'.join(negative_words), 'options': 'i'}}
#                             ]},
#                             'then': 'sad',
#                             'else': 'neutral'
#                         }
#                     }
#                 }
#             }
#         }
#     },
#     {
#         '$group': {
#             '_id': '$Date',
#             'happy': {'$sum': {'$cond': [{'$eq': ['$sentiment', 'happy']}, 1, 0]}},
#             'sad': {'$sum': {'$cond': [{'$eq': ['$sentiment', 'sad']}, 1, 0]}},
#             'neutral': {'$sum': {'$cond': [{'$eq': ['$sentiment', 'neutral']}, 1, 0]}}
#         }
#     },
#     {
#         '$sort': {'_id': 1}
#     }
# ]

#
# result = list(collection.aggregate(pipeline))

#
# dates = [entry['_id'] for entry in result]
# happy_counts = [entry['happy'] for entry in result]
# sad_counts = [entry['sad'] for entry in result]
# neutral_counts = [entry['neutral'] for entry in result]

#
# plt.figure(figsize=(15, 8))
# plt.plot(dates, happy_counts, label='Happy', marker='o')
# plt.plot(dates, sad_counts, label='Sad', marker='o')
# plt.plot(dates, neutral_counts, label='Neutral', marker='o')
# plt.title('Sentiment Trends Over Time')
# plt.xlabel('Date')
# plt.ylabel('Counts')
# plt.legend()
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# 
# client.close()

# ------------------------------Query 3 Data is in millions ---------------------------------------------------------------------------
# from pymongo import MongoClient
# import matplotlib.pyplot as plt


# client = MongoClient('mongodb://localhost:27017')
# db = client['nytimes']
# collection = db['article']

# pipeline = [
#     {
#         '$match': {"news_desk": "Sports"}
#     },
#     {
#         '$addFields': {
#             'pub_date': {'$toDate': '$pub_date'}
#         }
#     },
#     {
#         '$project': {
#             'year': {'$year': '$pub_date'},
#             'keywords': 1
#         }
#     },
#     {
#         '$unwind': '$keywords'
#     },
#     {
#         '$group': {
#             '_id': {'year': '$year', 'keyword': '$keywords.value'},
#             'counts': {'$sum': 1}
#         }
#     },
#     {
#         '$sort': {'_id.year': 1, 'counts': -1}
#     },
#     {
#         '$group': {
#             '_id': '$_id.year',
#             'top_keywords': {'$push': {'keyword': '$_id.keyword', 'counts': '$counts'}}
#         }
#     },
#     {
#         '$project': {
#             '_id': 0,
#             'year': '$_id',
#             'top_keywords': {'$slice': ['$top_keywords', 10]}
#         }
#     },
#     {
#         '$sort': {'year': 1} 
#     }
# ]

# result = list(collection.aggregate(pipeline))

# years = [entry['year'] for entry in result]
# top_keywords_data = [entry['top_keywords'] for entry in result]

# keyword_counts_by_year = {}

# for year, top_keywords in zip(years, top_keywords_data):
#     keyword_counts_by_year[year] = {}
#     for keyword_entry in top_keywords:
#         keyword = keyword_entry.get('keyword', '')  
#         counts = keyword_entry.get('counts', 0)   
#         keyword_counts_by_year[year][keyword] = counts

# plt.figure(figsize=(15, 8))

# for keyword in set(keyword for counts_by_year in keyword_counts_by_year.values() for keyword in counts_by_year.keys()):
#     counts_by_year = [keyword_counts_by_year[year].get(keyword, 0) for year in years]
#     plt.plot(years, counts_by_year, label=keyword)

# plt.title('Top Keywords Trends by Year (Sports Desk)')
# plt.xlabel('Year')
# plt.ylabel('Counts')
# plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
# plt.grid(True)
# plt.show()

# client.close()
