from kafka import KafkaProducer
import json
from mongo_extract import extract_from_mongo

def kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    df = extract_from_mongo()
    records = df.to_dict(orient='records')
    topic_name = 'air_topic'
    
    print(f"Producing {len(records)} records to Kafka topic '{topic_name}'")
    
    for record in records:
        producer.send(topic_name, value=record)
        
    producer.flush()
    print("All records have been sent to Kafka.")
    
kafka_producer()
        