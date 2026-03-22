from dotenv import load_dotenv
import os
load_dotenv()

import pandas as pd
import requests
from datetime import date
import time
import pymongo
from urllib.parse import quote_plus
from extract import extracting

def loading(combined_df):
    
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

    Airdata_dict = combined_df.to_dict(orient='records')
    collection.insert_many(Airdata_dict)
    
    print(f"Inserted {len(Airdata_dict)} records into '{collection_name}'")

    client.close()
    
while True:
  combined_df = extracting()
  loading(combined_df)
  print("Sleeping for 1 hour......")
  time.sleep(3600)