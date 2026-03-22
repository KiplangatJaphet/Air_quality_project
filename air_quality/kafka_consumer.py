from dotenv import load_dotenv
import os
load_dotenv()

from kafka import KafkaConsumer
import json
import psycopg2

def kafka_consumer_and_load():

    consumer = KafkaConsumer(
        'air_topic',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        group_id='air-quality-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x and x != b'' and x != b'\x00' else None
    )
    
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT")),
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD")
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Listening to Kafka topic 'air_topic'...")
    
    try:
        for message in consumer:
            data = message.value
            
            query = """
                INSERT INTO measurements (
                    city, time, pm2_5, pm10, ozone, carbon_monoxide,
                    nitrogen_dioxide, sulphur_dioxide, uv_index
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                data['city'], data['time'], data['pm2_5'], data['pm10'],
                data['ozone'], data['carbon_monoxide'], data['nitrogen_dioxide'],
                data['sulphur_dioxide'], data['uv_index']
            )
            
            cursor.execute(query, values)
            print(f"Inserted: {data['city']} at {data['time']}")
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        cursor.close()
        conn.close()
        consumer.close()

if __name__ == "__main__":
    kafka_consumer_and_load()
    