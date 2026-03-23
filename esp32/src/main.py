# Arquivo: src/main.py

import time
import json
import machine
from libs.wifi import WiFiConnector
from libs.mqtt import MQTTConnector
from libs.dht22 import DHT22Sensor
from libs.ldr import LDRSensor
from libs.pir import PIRSensor
from libs.relay import RelayControl

# --- Configurações de Hardware (Pinos) ---
PIN_DHT = 23
PIN_LDR = 34    # Entrada Analógica (ADC1_CH6)
PIN_PIR = 27    # Entrada Digital
PIN_RELAY = 2   # Saída Digital (LED Onboard do ESP32 costuma ser no 2 também)

# --- Configurações de Rede e MQTT ---
WIFI_SSID = "labiiot"
WIFI_PASSWORD = "lab@iiot"
MQTT_BROKER = "10.1.1.101" 
MQTT_CLIENT_ID = "esp32-smart-house-real"

# Tópicos FIWARE
API_KEY = "house123"
DEVICE_ID = "esp32_001"
TOPIC_ATTRS = f"/json/{API_KEY}/{DEVICE_ID}/attrs"
TOPIC_CMD = f"/json/{API_KEY}/{DEVICE_ID}/cmd"
TOPIC_CMDEXE = f"/json/{API_KEY}/{DEVICE_ID}/cmdexe"

# Intervalo de leitura
PUBLISH_INTERVAL = 5

# --- Lógica de Comandos ---

def command_callback(topic, msg):
    """
    Executa ações baseadas em comandos recebidos via MQTT.
    """
    print(f"\n[COMANDO] Recebido: {msg.decode()}")
    
    try:
        command_data = json.loads(msg.decode())
        response = {}
        
        for cmd_name, cmd_value in command_data.items():
            # Controle de Atuadores Reais
            if cmd_name == "lamp":
                if cmd_value == "on":
                    relay.on()
                else:
                    relay.off()
                print(f"Relé -> {relay.status()}")
                response[cmd_name] = "OK"
            
            # Simulados (Mantenha se o hardware ainda não estiver lá)
            elif cmd_name == "door" or cmd_name == "bell":
                print(f"Atuador Simulado '{cmd_name}' -> {cmd_value}")
                response[cmd_name] = "OK"
            
            else:
                response[cmd_name] = f"ERROR: '{cmd_name}' não mapeado."

        # Responder ao IoT Agent
        mqtt.publish(TOPIC_CMDEXE, json.dumps(response))

    except Exception as e:
        print(f"Erro no processamento de comando: {e}")

# --- Inicialização ---

def main():
    global mqtt, relay
    
    print("Iniciando Sistema com Hardware Real...")

    # Sensores Reais
    dht_sensor = DHT22Sensor(PIN_DHT)
    ldr_sensor = LDRSensor(PIN_LDR)
    pir_sensor = PIRSensor(PIN_PIR)
    relay = RelayControl(PIN_RELAY, active_low=False)

    # Conexões
    wifi = WiFiConnector(WIFI_SSID, WIFI_PASSWORD)
    if not wifi.connect():
        machine.reset()

    mqtt = MQTTConnector(MQTT_CLIENT_ID, MQTT_BROKER)
    mqtt.set_callback(command_callback)
    
    if not mqtt.connect():
        machine.reset()

    mqtt.subscribe(TOPIC_CMD)

    last_publish = 0

    # --- Loop Principal ---
    while True:
        try:
            mqtt.check_for_messages()

            if (time.time() - last_publish) >= PUBLISH_INTERVAL:
                # Leituras Reais
                dht_data = dht_sensor.read_data()
                luminosity = ldr_sensor.read_luminosity()
                presence = pir_sensor.is_present()

                if dht_data:
                    payload = {
                        "t": float(f"{dht_data['temperature']:.2f}"),
                        "h": float(f"{dht_data['humidity']:.2f}"),
                        "l": luminosity,
                        "p": presence
                    }
                    mqtt.publish(TOPIC_ATTRS, json.dumps(payload))
                    last_publish = time.time()
            
            time.sleep(0.1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
