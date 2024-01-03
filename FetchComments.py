import requests

api_key = "15MPlclMxKGuTa7WreSZ9IYcbjoo45sL"
article_url = "https://www.nytimes.com/2018/01/01/arts/mariah-carey-new-years-eve.html"

response = requests.get(
    "https://api.nytimes.com/svc/search/v2/articlesearch.json",
    params={"api-key": api_key, "fq": f"web_url:(\"{article_url}\")"}
)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()
    print(data)
    # Extract the article information
    if data["response"]["docs"]:
        article = data["response"]["docs"][0]
        # print("Headline:", article["headline"]["main"])
        # print("Publication Date:", article["pub_date"])
        # print("Snippet:", article["snippet"])
    else:
        print("No article found.")
else:
    print("Error:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))
