import machine
import dht

class DHT22Sensor:
    def __init__(self, pin):
        self.dht_sensor = dht.DHT22(machine.Pin(pin))

    def read_data(self):
        try:
            self.dht_sensor.measure()
            temperature = self.dht_sensor.temperature()
            humidity = self.dht_sensor.humidity()
            return temperature, humidity
        except OSError as e:
            print(f"Falha na leitura do sensor DHT22: {e}")
            return None, None
