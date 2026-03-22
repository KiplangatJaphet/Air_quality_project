from kafka import KafkaProducer
import json
import time
 # a testing kafka producer that generates sample air quality data
def kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    
    records = []
    cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
    
    for city in cities:
        record = {
            'city': city,
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'pm2_5': 20 + len(city),
            'pm10': 30 + len(city),
            'ozone': 0.05,
            'carbon_monoxide': 1.2,
            'nitrogen_dioxide': 0.03,
            'sulphur_dioxide': 0.01,
            'uv_index': 5
        }
        records.append(record)
    
    topic_name = 'air_topic'
    
    print(f"Producing {len(records)} records to Kafka topic '{topic_name}'")
    
    for record in records:
        producer.send(topic_name, value=record)
        print(f"Sent: {record['city']}")
        
    producer.flush()
    print("All records have been sent to Kafka.")
    
kafka_producer()