Here’s a detailed README file for the Kafka processing pipeline, including explanations of design choices, data flow, and considerations for efficiency, scalability, and fault tolerance.

---

# Kafka Data Processing Pipeline

## Overview

This project sets up a Kafka-based data processing pipeline using the Confluent Kafka Python client. The pipeline consumes messages from a Kafka topic, processes them, and then produces the processed messages to a new Kafka topic. The processing includes standardizing and filtering IP addresses, transforming data, and maintaining fault tolerance and efficiency.


## Table of Contents

1. [Design Choices](#design-choices)
2. [Data Flow](#data-flow)
3. [Pipeline Efficiency and Scalability](#pipeline-efficiency-and-scalability)
4. [Fault Tolerance](#fault-tolerance)
5. [Usage](#usage)
6. [Functions](#functions)
7. [Setup and Configuration](#setup-and-configuration)
8. [License](#license)

## Design Choices

### Kafka Topics

- **Source Topic (`user-login`)**: The Kafka topic from which messages are consumed. This topic contains raw data about user logins.
- **Destination Topic (`processed-data-topic`)**: The Kafka topic to which processed messages are produced.

### Data Processing

- **IP Standardization and Filtering**: IP addresses in the messages are standardized to ensure consistency and filtered to remove invalid IPs.
- **Data Transformation**: Messages are enhanced with additional fields like `processing_timestamp` and `processed` status. Timestamps are converted from UNIX epoch format to ISO format for readability.

### Efficiency

- **Batch Processing**: Messages are processed one at a time but can be adjusted for batch processing if required.
- **Polling Interval**: The consumer polls messages with a timeout interval of 1 second to balance between latency and processing load.

### Scalability

- **Consumer Group**: Kafka consumer groups enable scaling out by allowing multiple consumers to read from the same topic in parallel.
- **Producer Configuration**: Configured to handle high throughput and ensure reliable delivery of messages.

### Fault Tolerance

- **Error Handling**: Errors in message consumption or production are logged, and invalid messages are discarded.
- **Graceful Shutdown**: On keyboard interrupt or failure, the pipeline saves processed messages to a file and ensures that the Kafka consumer and producer are closed properly.

## Data Flow

1. **Message Consumption**: The consumer subscribes to the `user-login` topic and polls for new messages.
2. **Processing**: Each message is decoded, standardized (IP addresses), transformed, and filtered.
3. **Message Production**: The processed message is produced to the `processed-data-topic`.
4. **Persistence**: Processed messages are stored in a local JSON file for durability and recovery.

## Pipeline Efficiency and Scalability

- **Efficient Message Handling**: The pipeline uses Kafka's built-in message handling and delivery guarantees to ensure messages are processed and produced efficiently.
- **Scalability**: The use of Kafka consumer groups allows the system to scale horizontally by adding more consumers to handle increased load.
- **Configurable Polling**: The polling interval can be adjusted based on system performance and message arrival rate.

## Fault Tolerance

- **Error Logging**: Any errors encountered during message processing or production are logged to provide insight into potential issues.
- **Invalid Message Handling**: Messages with invalid IP addresses are filtered out and not processed further, preventing errors from propagating.
- **Graceful Shutdown**: The pipeline ensures that resources are released properly and that data is saved if the pipeline is stopped unexpectedly.

## Usage

1. **Install Dependencies**: Ensure the Confluent Kafka Python client and other dependencies are installed.
   ```bash
   pip install confluent_kafka pandas
   ```

2. **Run the Pipeline**: Execute the script to start the Kafka consumer and producer.
   ```bash
   python3 consumer.py
   ```

3. **Configuration**: Adjust the Kafka server configuration and topic names in the script as needed.

## Functions

### `standardize_ip(ip: str) -> str`
   - **Description**: Standardizes an IP address to its canonical form.
   - **Parameters**: `ip` (str): The IP address to standardize.
   - **Returns**: Canonical form of the IP address or `None` if invalid.

### `is_valid_ip(ip: str) -> bool`
   - **Description**: Checks if an IP address is valid.
   - **Parameters**: `ip` (str): The IP address to validate.
   - **Returns**: `True` if the IP address is valid, `False` otherwise.

### `process_message(message: str) -> str`
   - **Description**: Processes a message by standardizing IP addresses, adding new fields, and transforming data.
   - **Parameters**: `message` (str): The raw message in JSON format.
   - **Returns**: Processed message in JSON format or `None` if invalid.

## Setup and Configuration
## Setup

### Prerequisites

- Docker
- Docker Compose (if using a multi-container setup)
- Kafka and Zookeeper instances running

1. **Kafka Server**: Ensure Kafka and Zookeeper are running on `localhost:29092`. Adjust server addresses in the script if different.
2. **Topics**: Ensure the Kafka topics `user-login` and `processed-data-topic` are created and configured properly.
3. **JSON File**: The `processed_data.json` file is used to store processed messages locally. Ensure write permissions are available.Mainly done to understand data and pre-processing approach before storing it on new Kafka Topic.

### Kafka Topics Setup

Before running the application, you need to create the required Kafka topics. Use the following commands to set up the topics:

```bash
# Create the 'user-login' topic
docker exec -it kafka-container kafka-topics --create --topic user-login --bootstrap-server localhost:29092 --partitions 1 --replication-factor 1

# Create the 'processed-data-topic' topic
docker exec -it kafka-container kafka-topics --create --topic processed-data-topic --bootstrap-server localhost:29092 --partitions 1 --replication-factor 1

```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

This README provides an overview of the Kafka data processing pipeline, including design choices, data flow, efficiency, scalability, and fault tolerance, along with usage instructions and function details.
