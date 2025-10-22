import machine
import dht
import time

class DHT22Sensor:
    """
    Uma classe para interagir com o sensor de temperatura e umidade DHT22.
    """
    def __init__(self, pin):
        """
        Inicializa o sensor no pino especificado.
        
        :param pin: O número do pino GPIO ao qual o sensor está conectado.
        """
        dht_pin = machine.Pin(pin)
        self.sensor = dht.DHT22(dht_pin)
        print(f"Sensor DHT22 inicializado no pino {pin}.")

    def read_data(self):
        """
        Lê os dados de temperatura e umidade do sensor.
        
        :return: Um dicionário com 'temperature' e 'humidity' ou None em caso de falha.
        """
        try:
            self.sensor.measure()
            temp = self.sensor.temperature()
            hum = self.sensor.humidity()
            
            if temp is None or hum is None:
                print("Falha ao obter leitura. Verifique o sensor.")
                return None
                
            return {"temperature": temp, "humidity": hum}
            
        except OSError as e:
            print(f"Falha ao ler o sensor: {e}")
            return None

# Exemplo de uso:
if __name__ == "__main__":
    dht_sensor = DHT22Sensor(23)  # Inicializa o sensor no pino GPIO 23

    while True:
        dados = dht_sensor.read_data()
        
        if dados:
            print(f"Temperatura: {dados['temperature']:.2f}°C | Umidade: {dados['humidity']:.2f}%")
        
        time.sleep(2)

