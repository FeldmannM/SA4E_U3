# Michael Feldmann
import sys
import json
import subprocess

# Kafka Topic für jedes Segment erstellen
def create_topic(segment_id):
    try:
        cmd = [
            'docker', 'exec', 'kafka1',  # Ziel: Broker 1 für Topic-Administration
            'kafka-topics.sh',
            '--create',
            '--topic', segment_id,
            '--bootstrap-server', 'kafka1:9096, kafka2:9097, kafka3:9098', # Alle 3 Broker im Cluster anprechen
            '--replication-factor', '3',  # Replikation über alle 3 Broker
            '--partitions', '1',
            '--if-not-exists'
        ]
        subprocess.run(cmd, check=True)
        print(f"Successfully created topic: {segment_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating topic {segment_id}: {e}")

# Einzelnes Segment starten
def start_segment(segment):
    segment_id = segment['segmentId']
    next_segments = segment.get('nextSegments', [])
    seg_type = segment['type'] # neu Segmenttyp
    cmd = [
        'python', 'segment.py', segment_id
    ] + next_segments + [seg_type]  # Typ des Segments anhängen
    print(f"Starting segment: {cmd}")
    subprocess.Popen(cmd)


def main():
    if len(sys.argv) != 2:
        print("Usage: python configurator.py <track_description.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    for track in data['tracks']:
        for segment in track['segments']:
            create_topic(segment['segmentId'])
    
    for track in data['tracks']:
        for segment in track['segments']:
            start_segment(segment)

if __name__ == "__main__":
    main()
