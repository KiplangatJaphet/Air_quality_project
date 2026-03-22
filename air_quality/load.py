import pandas as pd
import requests
from datetime import date
import time
import pymongo
from urllib.parse import quote_plus
from extract import extracting

def loading(combined_df):
    
    
    password = "password123&4"
    encoded_password = quote_plus(password)
    
    mongo_url = f"mongodb+srv://kiplangatjaphet2:{encoded_password}@cluster0.b8r5142.mongodb.net/?appName=Cluster0"
    db_name = "air_quality_db"
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