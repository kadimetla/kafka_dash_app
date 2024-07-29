from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

categories = ['A', 'B', 'C']

while True:
    data = {
        'Category': categories,
        'Values': [random.randint(0, 100) for _ in categories]
    }
    producer.send('dash_topic', value=data)
    time.sleep(5)  # Send data every 5 seconds
