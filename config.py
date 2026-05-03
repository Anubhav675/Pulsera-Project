# Processing Constants 
SAMPLE_RATE_HZ = 250
SMA_WINDOW = 10
ADAPTIVE_THRESHOLD_OFFSET = 600
REFRACTORY_MS = 350
HYSTERESIS_THRESHOLD = 50
GRAPH_Y_OFFSET = 60
GRAPH_MAX_HEIGHT = 45
NOISE_FLOOR_RANGE = 1200

# Network Settings (Level 2 requirement)
WIFI_SSID = "2G"
WIFI_PASSWORD = "nepal12345"
MQTT_BROKER = "192.168.9.253"
MQTT_PORT = 5000  # FIXED: Correct Lab Port[cite: 2]

# MQTT Topics
TOPIC_DEVICE_ADD = b"database/devices/add"
TOPIC_PATIENT_ADD = b"database/patients/add"
TOPIC_RECORD_ADD = b"database/records/add"
TOPIC_KUBIOS_REQ = b"kubios/request"
TOPIC_KUBIOS_RES = b"kubios/response"


