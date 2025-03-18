# Michael Feldmann
import sys
import random
from kafka import KafkaConsumer, KafkaProducer
from threading import Lock, Thread
import time

# Nur einer darf sich im Bottleneck-Segment aufhalten
bottleneck_lock = Lock()

# Argumente auslesen
segment_id = sys.argv[1]
next_segments = sys.argv[2:-1]
seg_type = sys.argv[-1]

# Verlangsamung der Wagen
slow_down_time = random.randint(5, 10)
slow_down_count = 0

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

# Threading damit die Segmenttypen wie erwartet funktionieren
def process_vehicle(car_id, start_time, laps, round_count, segment_id, caesar_visited, token, next_segments):
    global slow_down_count, slow_down_time

    # Runde zählt bei Start-und-Ziel-Segment und Ceasar-Segment
    if segment_id.startswith("start-and-goal") or segment_id.startswith("caesar"):
        if int(round_count) == -1:
            # Startpunkt setzen
            round_count = 0
            print(f"Car {car_id} started at {segment_id}. First lap begins!")
        else:
            # Runde erhöhen
            round_count = int(round_count) + 1
            print(f"Car {car_id} completed lap {round_count}/{laps}.")
		# Wurde Caesar besucht?
        if segment_id.startswith("caesar"):
            caesar_visited = True
            print(f"Car {car_id} visited Caesar's sector at {segment_id}. This is mandatory!")
			
	# Bottleneck-Logik
    if seg_type == "bottleneck":
        with bottleneck_lock:
            print(f"Car {car_id} is entering bottleneck at {segment_id}.")
            wait_time = random.randint(1, 5)
            print(f"Car {car_id} is waiting for {wait_time} seconds in bottleneck.")
            time.sleep(wait_time)
            print(f"Car {car_id} is leaving bottleneck at {segment_id}.")
	
    # Slow-Down-Logik
    if seg_type == "slow-down":
        print(f"Car {car_id} is entering a slow-down zone. Cars must reduce speed!")
        slow_down_count += 1
        adjusted_slow_down_time = slow_down_time / slow_down_count
        print(f"Car {car_id} is delayed by {adjusted_slow_down_time} seconds at {segment_id}.")
        time.sleep(adjusted_slow_down_time)
        print(f"Car {car_id} is leaving the slow-down zone at {segment_id}.")

    # Prüfen, ob das Ziel (alle Runden) erreicht wurde
    if int(round_count) >= int(laps) and (segment_id.startswith("start-and-goal") or segment_id.startswith("caesar")):
        if caesar_visited:
            producer.send('finish_line', message.value)
            print(f"Car {car_id} finished the race after {round_count} laps!")
        else:
            print(f"Car {car_id} cannot finish the race without visiting Caesar! The car will continue to race until Caesar's sector is visited.")
			# Eine weitere Runde muss gefahren werden wenn Caesar nicht besucht wurde
            updated_token = f'{car_id}|{start_time}|{laps}|{round_count}|{segment_id}|{"False"}'.encode('utf-8')
            for next_segment in next_segments:
                producer.send(next_segment, updated_token)
                print(f"Message sent to next segment {next_segment}: {updated_token.decode('utf-8')}")
    else:
		# Zufällige Auswahl eines nächsten Segments
        if len(next_segments) > 1:
            chosen_index = random.randint(0, len(next_segments) - 1)
            chosen_segment = next_segments[chosen_index]
        else:
            # Nur ein Ziel verfügbar, wähle es
            chosen_segment = next_segments[0]
			
        #print(f"DEBUG: Available next segments: {next_segments}")
        #print(f"DEBUG: Randomly chosen segment: {chosen_segment}")
        print(f"Car {car_id} is heading to {chosen_segment} from {segment_id}.")
        if caesar_visited:
            updated_token = f'{car_id}|{start_time}|{laps}|{round_count}|{segment_id}|{"True"}'.encode('utf-8')
        else:
            updated_token = f'{car_id}|{start_time}|{laps}|{round_count}|{segment_id}|{"False"}'.encode('utf-8')
        producer.send(chosen_segment, updated_token)
        print(f"Message sent to next segment {chosen_segment}: {updated_token.decode('utf-8')}")
    producer.flush()


for message in consumer:
    token = message.value.decode('utf-8')
    # Erweitert
    car_id, start_time, laps, round_count, current_segment, caesar_visited = token.split('|')
    round_count = int(round_count)
    if(caesar_visited == "True"):
        caesar_visited = True
    else:
        caesar_visited = False
    # Starte einen separaten Thread für jedes Fahrzeug
    Thread(target=process_vehicle, args=(
        car_id, start_time, laps, round_count, segment_id, caesar_visited, token, next_segments
    )).start()