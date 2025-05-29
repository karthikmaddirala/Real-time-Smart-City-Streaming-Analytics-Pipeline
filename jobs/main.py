import os
from confluent_kafka import SerializingProducer
import simplejson as json
from datetime import datetime,  timedelta
import time
import random
import uuid

import numpy as np

REAL_COORDINATES = [
    {"latitude": 51.5074 + i * (52.4862 - 51.5074) / 999 + 0.01 * np.sin(i / 50),
     "longitude": -0.1278 + i * (-1.8904 + 0.1278) / 999 + 0.01 * np.cos(i / 50)}
    for i in range(1000)
]

STABLE_WEATHER_PRESETS = [
    {"temperature": 15.0, "condition": "Cloudy", "wind": 10, "humidity": 60, "aqi": 42},
    {"temperature": 18.5, "condition": "Sunny", "wind": 5, "humidity": 55, "aqi": 35},
    {"temperature": 12.3, "condition": "Rain", "wind": 14, "humidity": 80, "aqi": 58}
]

EMERGENCY_EVENT_INDEX = random.randint(300, 700)
EMERGENCY_EVENT_GENERATED = False

LONDON_COORDINATES = {"latitude": 51.5073, "longitude": -0.1278}
BERMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}


LATITUDE_INCREMENT = (BERMINGHAM_COORDINATES["latitude"]-LONDON_COORDINATES["latitude"])/100
LONGITUDE_INCREMENT = (BERMINGHAM_COORDINATES["longitude"]-LONDON_COORDINATES["longitude"])/100

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GSP_TOPIC = os.getenv('GSP_TOPIC', 'gsp_data')
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC', 'emergency_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_data')

random.seed(42)
start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds=60)
    return start_time


def generate_vehicle_data(device_id, timestamp,location):
    #location = simulate_vehicle_movement()
    timestamp = timestamp
    hour = timestamp.hour

    # Realistic driving speed based on time
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        speed = random.uniform(10, 25)  # Rush hour
    else:
        speed = random.uniform(25, 50)

    # Assume one car, consistent make/model
    make, model = 'BMW', 'M5'
    fuel_type = 'Hybrid'

    direction = 'North-West'  # since we're simulating movement from London to Birmingham

    return {
        'id': uuid.uuid4(),  # Unique event ID
        'deviceId': device_id,
        'timestamp': timestamp.isoformat(),
        'location': f"({round(location[0], 6)}, {round(location[1], 6)})",
        'speed': round(speed, 2),
        'direction': direction,
        'make': make,
        'model': model,
        'year': 2024,
        'fuelType': fuel_type
    }


def generate_gps_data(device_id, timestamp):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': timestamp.isoformat(),
        'speed': round(random.uniform(25, 50), 2),  # should mostly match vehicle speed
        'direction': 'North-West',
        'vehicleType': 'private'
    }


def generate_traffic_camera_data(device_id, timestamp, location, camera_id='UK-CAM-001'):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'cameraId': camera_id,
        'location': f"({round(location[0], 6)}, {round(location[1], 6)})",
        'timestamp': timestamp.isoformat(),
        'snapshot': 'data:image/jpeg;base64,...'  # Simulated placeholder
    }

def generate_weather_data(device_id, timestamp, location, step_index=0):
    preset = STABLE_WEATHER_PRESETS[(step_index // 100) % len(STABLE_WEATHER_PRESETS)]
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'location': f"({round(location[0], 6)}, {round(location[1], 6)})",
        'timestamp': timestamp.isoformat(),
        'temperature': round(preset["temperature"] + random.uniform(-0.5, 0.5), 2),
        'weatherCondition': preset["condition"],
        'precipitation': round(random.uniform(0, 5), 2) if preset["condition"] == "Rain" else 0.0,
        'windSpeed': round(preset["wind"] + random.uniform(-2, 2), 2),
        'humidity': min(max(preset["humidity"] + random.randint(-5, 5), 0), 100),
        'airQualityIndex': round(preset["aqi"] + random.uniform(-3, 3), 2)
    }


def generate_emergency_incident_data(device_id, timestamp, location, step_index=0):
    global EMERGENCY_EVENT_GENERATED
    if step_index == EMERGENCY_EVENT_INDEX and not EMERGENCY_EVENT_GENERATED:
        EMERGENCY_EVENT_GENERATED = True
        incident_type = random.choice(['Accident', 'Fire', 'Medical'])
        return {
            'id': uuid.uuid4(),
            'deviceId': device_id,
            'incidentId': uuid.uuid4(),
            'type': incident_type,
            'timestamp': timestamp.isoformat(),
            'location': f"({round(location[0], 6)}, {round(location[1], 6)})",
            'status': 'Active',
            'description': f'{incident_type} reported'
        }
    else:
        return {
            'id': uuid.uuid4(),
            'deviceId': device_id,
            'incidentId': uuid.uuid4(),
            'type': 'None',
            'timestamp': timestamp.isoformat(),
            'location': f"({round(location[0], 6)}, {round(location[1], 6)})",
            'status': 'Resolved',
            'description': 'No incident'
        }


def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    #raise TypeError(f'Object of type {obj.__class__.name} is not JSON serializable')

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition}]')

def produce_data_to_kafka(producer, topic, data):
    producer.produce(topic, 
                     key=str(data['id']),
                     value=json.dumps(data, default=json_serializer).encode('utf8'),
                     on_delivery = delivery_report
                     )
    producer.flush()

def simulate_journey(producer, device_id):
    step_index = 0
    for location in REAL_COORDINATES:
        timestamp = get_next_time()
        vehicle_data = generate_vehicle_data(device_id,timestamp,(location['latitude'], location['longitude']))
        gps_data = generate_gps_data(device_id, timestamp)
        traffic_camera_data = generate_traffic_camera_data(device_id, timestamp, (location['latitude'], location['longitude']))
        weather_data = generate_weather_data(device_id, timestamp, (location['latitude'], location['longitude']), step_index)
        emergency_incident_data = generate_emergency_incident_data(device_id, timestamp, (location['latitude'], location['longitude']), step_index)

        if (location['latitude'] >= 52.4862 and location['longitude'] <= -1.8904):
            print('Vehicle has reached Birmingham. Simulation ending...')
            break

        produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
        produce_data_to_kafka(producer, GSP_TOPIC, gps_data)
        produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_camera_data)
        produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
        produce_data_to_kafka(producer, EMERGENCY_TOPIC, emergency_incident_data)
        print("----------------------------------------------------------------")
        time.sleep(30)
        step_index += 1


if __name__ == '__main__':

    producer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'error_cb': lambda err: print(f'Kafka error: {err}')  
    }

    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer, 'Vechile-Kar-123')
    except KeyboardInterrupt:
        print('Simulation eded by the user')
    except Exception as e:
        print(f'Unexpected Error occurred: {e}')