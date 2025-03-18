# Michael Feldmann
import sys
from kafka import KafkaConsumer, KafkaProducer

# Argumente auslesen
segment_id = sys.argv[1]
next_segments = sys.argv[2:]

# Initialisiere Consumer für das aktuelle Segment
consumer = KafkaConsumer(
    segment_id,
    bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'], # Alle 3 Broker im Cluster anprechen
    auto_offset_reset='earliest',
    group_id=f"group-{segment_id}"
)

# Initialisiere Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'] # Alle 3 Broker im Cluster anprechen
)

print(f"Listening to {segment_id} for messages...")

for message in consumer:
    token = message.value.decode('utf-8')
    car_id, start_time, laps, round_count, current_segment = token.split('|')

    # Runde zählt bei Start-und-Ziel-Segment
    if segment_id.startswith("start-and-goal"):
        if int(round_count) == -1:
            # Startpunkt setzen
            round_count = 0
            print(f"Car {car_id} started at {segment_id}. First lap begins!")
        else:
            # Runde erhöhen
            round_count = int(round_count) + 1
            print(f"Car {car_id} completed lap {round_count}/{laps}.")

    # Prüfen, ob das Ziel (alle Runden) erreicht wurde
    if int(round_count) >= int(laps):
        producer.send('finish_line', message.value)
        print(f"Car {car_id} finished the race after {round_count} laps!")
    else:
        # Token mit aktualisiertem Runden-Zähler weiterleiten
        updated_token = f'{car_id}|{start_time}|{laps}|{round_count}|{segment_id}'.encode('utf-8')
        for next_segment in next_segments:
            producer.send(next_segment, updated_token)
            print(f"Message sent to next segment {next_segment}: {updated_token.decode('utf-8')}")
    producer.flush()
