"""
Autor: Rafael Gomes Alves
Descrição: Módulo simples de exemplo de um DHT11/22 enviando dados via MQTT para um ESP32 com MicroPython.
Dispositivos: ESP32, DHT11/22, placa de prototipagem, resistores, cabos jumper.
"""

import time
import machine
from ..lib.sensores.dht_sensor import DHT22Sensor
from ..lib.mqtt.mqtt_client import MQTT

# --- Configurações ---
DHT_PIN = 4
MQTT_BROKER = "10.1.1.101"
MQTT_PORT = 1883
TOPIC_TEMP = b"casa/sala/temperatura"
TOPIC_HUMIDITY = b"casa/sala/umidade"
INTERVALO = 10  # Intervalo de publicação em segundos

def main():
    """Função principal."""
    sensor = DHT22Sensor(DHT_PIN)
    mqtt_client = MQTT(MQTT_BROKER, MQTT_PORT)

    if not mqtt_client.connect():
        print("Não foi possível conectar ao MQTT. Reiniciando em 5 segundos.")
        time.sleep(5)
        machine.reset()

    while True:
        temperature, humidity = sensor.read_data()

        if temperature is not None and humidity is not None:
            print(f"Publicando: Temp={temperature:.1f}C, Umidade={humidity:.1f}%")
            
            if not mqtt_client.publish(TOPIC_TEMP, str(temperature).encode()):
                print("Tentando reconectar ao MQTT...")
                if mqtt_client.connect():
                    print("Reconectado.")
                else:
                    print("Falha na reconexão. Reiniciando em 5 segundos.")
                    time.sleep(5)
                    machine.reset()

            if not mqtt_client.publish(TOPIC_HUMIDITY, str(humidity).encode()):
                print("Tentando reconectar ao MQTT...")
                if mqtt_client.connect():
                    print("Reconectado.")
                else:
                    print("Falha na reconexão. Reiniciando em 5 segundos.")
                    time.sleep(5)
                    machine.reset()
        
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()