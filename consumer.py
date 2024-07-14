from confluent_kafka import Consumer, Producer
import json
import os
import datetime
import ipaddress
import pandas as pd


# Configure the Consumer
consumer_config = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'fetch-consumer-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_config)
consumer.subscribe(['user-login'])

# Configure the Producer
producer_config = {
    'bootstrap.servers': 'localhost:29092'
}
producer = Producer(producer_config)

# List to store processed messages
processed_messages = []
device_type_counts = {}
locale_counts = {}
hourly_counts = {}

# Function to load existing messages from JSON file
def load_existing_messages(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def delivery_report(err, msg):
    """ Delivery report handler called on successful or failed delivery of message """
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def standardize_ip(ip: str) -> str:
    try:
        # Create an IP address object, which automatically normalizes the address
        ip_obj = ipaddress.ip_address(ip)
        # Return the canonical form of the IP address
        return ip_obj.exploded
    except ValueError:
        # Return None if the IP address is invalid
        return None

def is_valid_ip(ip: str) -> bool:
    try:
        # Create an IP address object to check validity
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Return False if the IP address is invalid
        return False

# Load existing messages if the file exists
        
existing_messages = load_existing_messages('processed_data.json')
processed_messages.extend(existing_messages)

def process_message(message):

    #Transform the message by adding a new field
    data = json.loads(message)
    data['processed'] = True

    # Data Validation Checks
    if 'user_id' not in data or 'timestamp' not in data:
        return None
    
    data['processing_time'] = datetime.datetime.now().isoformat()
    data['locale'] = data['locale'].upper()  # Standardize locale code

    # Convert timestamp to readable format
    if 'timestamp' in data:
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s').isoformat()
    
    #Check and standardize IP address format
    if 'ip' in data:
        data['ip'] = standardize_ip(data['ip'])  # Assume you have a function to standardize IP
    
    # Filter out invalid records
    if not is_valid_ip(data.get('ip', '')):
        return None
    

    return json.dumps(data)


try:
    while True:
        msg = consumer.poll(1.0)  # timeout in seconds
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        message = msg.value().decode('utf-8')
        #print(f"Received message: {len(message)}")

        processed_message = process_message(message)

        if processed_message:

            # Append the processed message to the list

            processed_messages.append(processed_message)
            print(f"Writing Processed message: {len(processed_messages)}")


            # Produce the processed message to the new Kafka topic
            producer.produce(
                'processed-data-topic',
                key=msg.key(),
                value=json.dumps(processed_message).encode('utf-8'),
                callback=delivery_report
            )
            producer.poll(0)

except KeyboardInterrupt:
    pass
finally:
    '''
    # Save processed messages to a JSON file
    with open('processed_data.json', 'w') as f:
        json.dump(processed_messages, f, indent=4)
    '''
    
    # Leave group and commit final offsets
    consumer.close()
    producer.flush()

