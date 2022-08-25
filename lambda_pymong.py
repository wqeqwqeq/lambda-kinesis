from urllib.parse import quote_plus

username = quote_plus("<wqeq>")
password = quote_plus("<wqeqsada2131>")
print(username, password)


import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient(
    f"mongodb+srv://<{username}>:<{password}>@cluster0.rcyqsmm.mongodb.net/?retryWrites=true&w=majority"
)
db = client["sample_analytics"]
print(db)
