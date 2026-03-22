import pandas as pd
import requests
from datetime import date

def extracting():
    cities = [
        {"name": "Nairobi", "latitude": -1.286389, "longitude": 36.817223},
        {"name": "Mombasa", "latitude": -4.0435, "longitude": 39.6682}
    ]
    
    combined_data = []
    for city in cities:
        api_url = (
              f"https://air-quality-api.open-meteo.com/v1/air-quality?"
              f"latitude={city['latitude']}&longitude={city['longitude']}&"
              f"hourly=pm2_5,pm10,ozone,carbon_monoxide,"
              f"nitrogen_dioxide,sulphur_dioxide,uv_index"
        )
        response = requests.get(api_url)
        data = response.json()
        
        new_df = pd.DataFrame({
        'city': city['name'],
        'longitude': data['longitude'],
        'latitude': data['latitude'],
        'time': data['hourly']['time'],
        'pm2_5': data['hourly']['pm2_5'],
        'pm10': data['hourly']['pm10'],
        'ozone': data['hourly']['ozone'],
        'carbon_monoxide': data['hourly']['carbon_monoxide'],
        'nitrogen_dioxide': data['hourly']['nitrogen_dioxide'],
        'sulphur_dioxide': data['hourly']['sulphur_dioxide'],
        'uv_index': data['hourly']['uv_index']
        })
        
        combined_data.append(new_df)
    
    
    combined_df = pd.concat(combined_data, ignore_index=True)
    return combined_df