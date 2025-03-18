# Michael Feldmann
import sys
from kafka import KafkaProducer
import time

# Argumente auslesen
segment_id = sys.argv[1]
laps = int(sys.argv[2])
car_id = sys.argv[3]

# Kafka-Producer initialisieren
try:
    producer = KafkaProducer(bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094']) # Alle 3 Broker im Cluster anprechen
    print("Kafka Producer successfully initialized")
except Exception as e:
    print(f"Error initializing Kafka Producer: {e}")
    sys.exit(1)

# Token initialisieren mit Runden-Zähler
token = f'{car_id}|{time.time()}|{laps}|-1|{segment_id}'.encode('utf-8')

# Debugging-Ausgabe für den Token
print(f"Initialized token: {token.decode('utf-8')}")
print(f"Message size: {len(token)} bytes")

# Wagen ins Rennen schicken
try:
    future = producer.send(segment_id, token)
    record_metadata = future.get(timeout=10)  # Warten auf Bestätigung vom Broker
    print(f"Message successfully sent to {segment_id}")
    print(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
except Exception as e:
    print(f"Error sending message to {segment_id}: {e}")
finally:
    producer.flush()
    producer.close()
