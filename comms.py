import network
import time
import ujson
import ubinascii
from umqtt.simple import MQTTClient
import config


class CommsManager:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)
        self._client = None
        self._latest_msg = None

        self._mac = self._get_mac()
        self._patient_id = None

    def _get_mac(self):
        self._wlan.active(True)
        return ubinascii.hexlify(self._wlan.config("mac")).decode().upper()

    def get_mac(self):
        return self._mac

    def _callback(self, topic, msg):
        print("\n=== MQTT RECEIVED ===")
        print("TOPIC:", topic)
        print("RAW:", msg)

        try:
            parsed = ujson.loads(msg)
            print("PARSED:", parsed)
            self._latest_msg = parsed
        except Exception as e:
            print("Parse error:", e)

    def connect_wifi(self):
        self._wlan.active(True)

        if self._wlan.isconnected():
            print("WiFi already connected:", self._wlan.ifconfig())
            return True

        print("Connecting WiFi...")
        self._wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        start = time.ticks_ms()
        while not self._wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > 15000:
                print("WiFi FAILED")
                return False
            time.sleep_ms(300)

        print("WiFi Connected:", self._wlan.ifconfig())
        return True

    def connect_mqtt(self):
        self._client = MQTTClient(self._mac, config.MQTT_BROKER, port=config.MQTT_PORT)
        self._client.set_callback(self._callback)
        self._client.connect()

        self._client.subscribe(b"kubios/response")
        self._client.subscribe(b"database/response")

        print("MQTT Connected")
        return True

    def _wait_msg(self, timeout=5000):
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < timeout:
            self._client.check_msg()

            if self._latest_msg:
                msg = self._latest_msg
                self._latest_msg = None
                return msg

            time.sleep_ms(200)

        return None

    def register_device(self):
        payload = {
            "mac": self._mac,
            "device_name": config.PROJECT_NAME
        }

        self._client.publish(config.TOPIC_DEVICE_ADD, ujson.dumps(payload))
        print("Registering device...")

        res = self._wait_msg()
        print("Device response:", res)

    def register_patient(self):
        payload = {
            "mac": self._mac,
            "patient_name": config.PATIENT_NAME
        }

        self._client.publish(config.TOPIC_PATIENT_ADD, ujson.dumps(payload))
        print("Registering patient...")

        res = self._wait_msg()

        if res and res.get("message") == "OK":
            self._patient_id = res.get("data")
            print("Patient ID:", self._patient_id)
        else:
            print("Patient registration failed")

    def save_to_db(self, hr, rmssd, sdnn, pns=None, sns=None, ppi=None):
        payload = {
            "mac": self._mac,
            "timestamp": int(time.time()),
            "mean_hr": int(hr),
            "mean_ppi": int(ppi) if ppi else 0,
            "rmssd": int(rmssd),
            "sdnn": int(sdnn)
        }

        if pns is not None:
            payload["pns"] = pns
        if sns is not None:
            payload["sns"] = sns
        if self._patient_id:
            payload["patient_id"] = self._patient_id

        print("Sending to DB:", payload)

        self._client.publish(config.TOPIC_RECORD_ADD, ujson.dumps(payload))

        res = self._wait_msg()
        print("DB response:", res)

    def request_analysis(self, rris):
        payload = {
            "mac": self._mac,
            "type": "RRI",
            "data": rris,
            "analysis": {"type": "readiness"}
        }

        print("Sending to Kubios...")
        self._client.publish(config.TOPIC_KUBIOS_REQ, ujson.dumps(payload))

        res = self._wait_msg(20000)
        return res

    def setup(self):
        if not self.connect_wifi():
            return False

        self.connect_mqtt()

        self.register_patient()
        time.sleep(1)
        self.register_device()

        return True
