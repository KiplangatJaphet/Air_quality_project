import pymongo
import pandas as pd
from datetime import date
from urllib.parse import quote_plus

def extract_from_mongo():
    
    password = "password123&4"
    encoded_password = quote_plus(password)
    
    mongo_url = f"mongodb+srv://kiplangatjaphet2:{encoded_password}@cluster0.b8r5142.mongodb.net/?appName=Cluster0"
    db_name = "air_quality_db"
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