# Arquivo: src/main.py

import time
import json
import machine
from libs.wifi import WiFiConnector
from libs.mqtt import MQTTConnector
from libs.dht22 import DHT22Sensor

# --- Configurações ---

# Wi-Fi
WIFI_SSID = "labiiot"
WIFI_PASSWORD = "lab@iiot"

# Broker MQTT
MQTT_BROKER = "10.1.1.101"  # Ex: "192.168.1.10"
MQTT_CLIENT_ID = "esp32-dht22-client"
MQTT_TOPIC = "/json/4jggok/urn:ngsi-ld:DHT22:001/attrs"
# Se o seu broker exigir autenticação, descomente e preencha as linhas abaixo
# MQTT_USER = "seu_usuario"
# MQTT_PASSWORD = "sua_senha"

# Sensor DHT22
DHT_PIN = 23  # Pino GPIO onde o sensor DHT22 está conectado (ex: D4)

# Intervalo de leitura e publicação (em segundos)
PUBLISH_INTERVAL = 2

# --- Lógica Principal ---

def main():
    """
    Função principal que executa a lógica do dispositivo.
    """
    print("Iniciando dispositivo ESP32...")

    # 1. Conectar ao Wi-Fi
    wifi = WiFiConnector(WIFI_SSID, WIFI_PASSWORD)
    if not wifi.connect():
        print("Não foi possível conectar ao Wi-Fi. Reiniciando em 10 segundos...")
        time.sleep(10)
        machine.reset()

    # 2. Inicializar o sensor DHT22
    sensor = DHT22Sensor(DHT_PIN)

    # 3. Conectar ao Broker MQTT
    # Certifique-se de passar user e password se o seu broker exigir
    mqtt = MQTTConnector(MQTT_CLIENT_ID, MQTT_BROKER)
    if not mqtt.connect():
        print("Não foi possível conectar ao broker MQTT. Reiniciando em 10 segundos...")
        time.sleep(10)
        machine.reset()

    print("\n--- Início da Operação ---")
    print(f"Publicando dados no tópico: '{MQTT_TOPIC}'")
    print(f"Intervalo de publicação: {PUBLISH_INTERVAL} segundos")

    # 4. Loop principal
    while True:
        try:
            # Ler dados do sensor
            sensor_data = sensor.read_data()

            if sensor_data:
                # Formatar payload JSON
                payload = {
                    "t": float(f"{sensor_data["temperature"]:.2f}"),
                    "h": float(f"{sensor_data["humidity"]:.2f}")
                }
                payload_str = json.dumps(payload)

                # Publicar no MQTT
                mqtt.publish(MQTT_TOPIC, payload_str)
            
            # Aguardar o próximo ciclo
            print(f"Aguardando {PUBLISH_INTERVAL} segundos para a próxima leitura...")
            time.sleep(PUBLISH_INTERVAL)

        except KeyboardInterrupt:
            print("Operação interrompida pelo usuário.")
            break
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            print("Tentando se recuperar e continuar...")
            time.sleep(10) # Pausa antes de tentar novamente

    # Desconectar (se o loop for quebrado)
    mqtt.disconnect()
    wifi.disconnect()
    print("Dispositivo finalizado.")

# Ponto de entrada do programa
if __name__ == "__main__":
    main()
