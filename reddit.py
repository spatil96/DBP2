import requests
import pymongo

CLIENT_ID = ''
SECRET_KEY = ''

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

data = {
    'grant_type': 'password',
    'username': '',
    'password': ''
}

headers = {'User-Agent': ''}
res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
print(res.json())
TOKEN = res.json()['access_token']
headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}
headers

link = "https://oauth.reddit.com/r/spotify/"
res = requests.get('https://oauth.reddit.com/r/spotify/', headers=headers)
res.json()

try:
    conn = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    print("Connected successfully to Reddit Database!!!")
except:  
    print("Could not connect to MongoDB")
db = conn.DataBase
collection = db.Reddit_data

post_list = res.json()['data']['children']
i = len(post_list)
if len(post_list) > 0:
    for post in post_list:
        collection.insert_one({"id":i,"post":post['data']['title']})