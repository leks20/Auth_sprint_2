import json

import requests

response = requests.get("http://localhost:9200/movies/_search")

data = response.json()

genres = []
for _ in data["hits"]["hits"]:
    print(_["_source"])
    genres.append(_["_source"])

print(genres)

genres_json = json.dumps(genres, indent=4)

with open("movies_data.json", "w") as file:
    file.write(genres_json)
