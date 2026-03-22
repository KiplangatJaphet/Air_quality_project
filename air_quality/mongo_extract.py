from dotenv import load_dotenv
import os
load_dotenv()

import pymongo
import pandas as pd
from datetime import date
from urllib.parse import quote_plus

def extract_from_mongo():
    
    password = os.getenv("MONGO_PASSWORD")
    user = os.getenv("MONGO_USER")
    cluster = os.getenv("MONGO_CLUSTER")
    encoded_password = quote_plus(password)
    
    mongo_url = f"mongodb+srv://{user}:{encoded_password}@{cluster}/?appName=Cluster0"
    db_name = os.getenv("MONGO_DB")
    collection_name = f"measurements{date.today()}"  

    client = pymongo.MongoClient(mongo_url)
    db = client[db_name]
    collection = db[collection_name]

    data = list(collection.find({}, {'_id': 0})) 
    df = pd.DataFrame(data)

    print(f"Fetched {len(df)} records from '{collection_name}'")

    client.close()
    return df

df = extract_from_mongo()
print(df.head())