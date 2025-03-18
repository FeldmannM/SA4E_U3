# Michael Feldmann
from kafka import KafkaConsumer
import time

# Initialisiere Consumer zum Abfragen der Ergebnisse
consumer = KafkaConsumer(
    'finish_line',
    bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'], # Alle 3 Broker im Cluster anprechen
    auto_offset_reset='earliest',
    group_id=None
)

for message in consumer:
    token = message.value.decode('utf-8')
    car_id, start_time, laps, round_count = token.split('|')[:4]
    total_time = time.time() - float(start_time)
    print(f'Wagen {car_id} hat das Rennen in {total_time:.2f} Sekunden beendet.')
