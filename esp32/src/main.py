# Arquivo: src/main.py

import time
import json
import machine
from libs.wifi import WiFiConnector
from libs.mqtt import MQTTConnector
from libs.dht22 import DHT22Sensor
from libs.ldr import LDRSensor
from libs.relay import RelayControl

# --- Configurações do Evento ---
# Escolha o perfil: "SIMPLE" (Apenas DHT22) ou "COMPLEX" (DHT22 + LDR + Relay)
PROFILE = "COMPLEX" 

# --- Configurações de Hardware (Pinos) ---
PIN_DHT = 23
PIN_LDR = 34    
PIN_RELAY = 2   # LED onboard ou Relé externo

# --- Configurações de Rede e MQTT ---
WIFI_SSID = "labiiot"
WIFI_PASSWORD = "lab@iiot"
MQTT_BROKER = "10.1.1.101" 

# Gera um ID único baseado no hardware da ESP32 (MAC Address ou Unique ID)
import ubinascii
UNIQUE_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Configurações FIWARE
API_KEY = "feiportas"
# O DEVICE_ID agora é prefixado pelo perfil + parte do ID único para ser representativo
DEVICE_ID = f"esp32_{PROFILE.lower()}_{UNIQUE_ID[-4:]}"

TOPIC_ATTRS = f"/json/{API_KEY}/{DEVICE_ID}/attrs"
TOPIC_CMD = f"/json/{API_KEY}/{DEVICE_ID}/cmd"
TOPIC_CMDEXE = f"/json/{API_KEY}/{DEVICE_ID}/cmdexe"

# --- Variáveis de Controle ---
PUBLISH_INTERVAL = 5
LDR_THRESHOLD = 1500 # Valor para automação local (opcional)
TEMP_THRESHOLD = 30.0 # Se a temperatura subir muito, liga a lâmpada (simulando ventoinha)
AUTO_MODE = True     # Se True, o ESP controla a lâmpada sozinho

# --- Lógica de Comandos ---

def command_callback(topic, msg):
    global AUTO_MODE
    print(f"\n[COMANDO] Recebido: {msg.decode()}")
    
    try:
        command_data = json.loads(msg.decode())
        response = {}
        
        for cmd_name, cmd_value in command_data.items():
            if cmd_name == "lamp":
                # Ao receber um comando manual, desativamos o modo automático temporariamente? 
                # Ou apenas obedecemos. Vamos obedecer.
                if cmd_value == "on":
                    relay.on()
                else:
                    relay.off()
                response[cmd_name] = "OK"
                print(f"Lâmpada -> {relay.status()}")
            
            elif cmd_name == "auto":
                AUTO_MODE = (cmd_value == "on")
                response[cmd_name] = "OK"
                print(f"Modo Automático -> {AUTO_MODE}")

        mqtt.publish(TOPIC_CMDEXE, json.dumps(response))

    except Exception as e:
        print(f"Erro no comando: {e}")

# --- Inicialização ---

def main():
    global mqtt, relay, AUTO_MODE
    
    print(f"--- FEI Portas Abertas | Perfil: {PROFILE} ---")

    # Inicialização de Sensores conforme Perfil
    dht_sensor = DHT22Sensor(PIN_DHT)
    
    if PROFILE == "COMPLEX":
        ldr_sensor = LDRSensor(PIN_LDR)
        relay = RelayControl(PIN_RELAY, active_low=False)
    
    # Conexões
    wifi = WiFiConnector(WIFI_SSID, WIFI_PASSWORD)
    if not wifi.connect():
        print("Falha no WiFi. Reiniciando...")
        time.sleep(5)
        machine.reset()

    mqtt = MQTTConnector(f"esp32_{DEVICE_ID}", MQTT_BROKER)
    mqtt.set_callback(command_callback)
    
    if not mqtt.connect():
        print("Falha no MQTT. Reiniciando...")
        time.sleep(5)
        machine.reset()

    if PROFILE == "COMPLEX":
        mqtt.subscribe(TOPIC_CMD)

    last_publish = 0

    # --- Loop Principal ---
    while True:
        try:
            mqtt.check_for_messages()

            if (time.time() - last_publish) >= PUBLISH_INTERVAL:
                # 1. Leitura de Sensores
                dht_data = dht_sensor.read_data()
                payload = {}

                if dht_data:
                    payload["t"] = float(f"{dht_data['temperature']:.2f}")
                    payload["h"] = float(f"{dht_data['humidity']:.2f}")

                if PROFILE == "COMPLEX":
                    luminosity = ldr_sensor.read_luminosity()
                    payload["l"] = luminosity
                    
                    # Lógica Automática Local (Luz ou Calor)
                    if AUTO_MODE:
                        temp = dht_data['temperature'] if dht_data else 0
                        if luminosity < LDR_THRESHOLD or temp > TEMP_THRESHOLD:
                            relay.on()
                        else:
                            relay.off()

                # 2. Publicação
                if payload:
                    print(f"Publicando: {payload}")
                    mqtt.publish(TOPIC_ATTRS, json.dumps(payload))
                
                last_publish = time.time()
            
            time.sleep(0.1)

        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(5)
            # Tentar reconectar se necessário
            if not wifi.is_connected():
                wifi.connect()
            if not mqtt.is_connected():
                mqtt.connect()

if __name__ == "__main__":
    main()

