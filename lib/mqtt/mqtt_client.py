from umqtt.simple import MQTTClient
import ubinascii
import machine

class MQTT:
    def __init__(self, broker, port):
        self.broker = broker
        self.port = port
        self.client_id = ubinascii.hexlify(machine.unique_id())
        self.client = MQTTClient(self.client_id, self.broker, port=self.port)

    def connect(self):
        try:
            self.client.connect()
            print(f"Conectado ao broker MQTT em {self.broker}")
            return True
        except OSError as e:
            print(f"Falha ao conectar ao broker MQTT: {e}")
            return False

    def publish(self, topic, message):
        try:
            self.client.publish(topic, message)
            return True
        except OSError as e:
            print(f"Falha ao publicar mensagem: {e}")
            return False

    def disconnect(self):
        self.client.disconnect()
