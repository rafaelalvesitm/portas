import threading
import os
import logging
import sys
import argparse
import dotenv

from lib.mqtt_client import MqttClient
from lib.dht22 import DHT22
from lib.pump import Pump
from lib.moisture import Moisture

# Defini constantes
ENV_FILE = ".env"

def main():
    
    # Define as chaves de acesso dos dispositivos a serem utilizadas no IoT Agent
    DHT22_SENSOR_KEY = os.environ.get("DHT22_SENSOR_KEY")
    PUMP_ACTUATOR_KEY = os.environ.get("PUMP_ACTUATOR_KEY")
    MOISTURE_SENSOR_KEY = os.environ.get("MOISTURE_SENSOR_KEY")

    # Define os IDs dos dispositivos a serem utilizados no IoT Agent
    DHT22_SENSOR_ID_1 = os.environ.get("DHT22_SENSOR_ID_1")
    PUMP_SENSOR_ID_1 = os.environ.get("PUMP_ACTUATOR_ID_1")
    MOISTURE_SENSOR_ID_1 = os.environ.get("MOISTURE_SENSOR_ID_1")

    # --- Define o cliente MQTT com suas funcionalidades ---
    mqtt_client = MqttClient()

    # --- Define os dispositivos ---
    # Sensor DHT22 
    dht22_sensor_1 = DHT22(mqtt_client, DHT22_SENSOR_KEY, DHT22_SENSOR_ID_1)

    # Pump actuator
    pump_actuator_1 = Pump(mqtt_client, PUMP_ACTUATOR_KEY, PUMP_SENSOR_ID_1)

    # Moisture sensor
    Moisture_sensor_1 = Moisture(mqtt_client, MOISTURE_SENSOR_KEY, MOISTURE_SENSOR_ID_1)

    # --- Define as threads para cada dispositivo ---
    threads = []

    threads.append(threading.Thread(target=dht22_sensor_1.run, daemon=True))
    threads.append(threading.Thread(target=pump_actuator_1.run, daemon=True))
    threads.append(threading.Thread(target=Moisture_sensor_1.run, daemon=True))

    # Inicia todas as threads
    for thread in threads:
        thread.start()

    # --- Mantém a thread principal funcionando ---
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Ctrl+C pressed")
        logging.info("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    # --- Defini os argumentos da linha de comando ---
    parser = argparse.ArgumentParser(description="Executa sensores e atuadores")
    parser.add_argument(
        "-d", "--debug", help="Habilita o modo de debug", default=False, action="store_true"
    )

    args = parser.parse_args()

    # --- Define o tipo de log ---
    log_level = (
        logging.DEBUG if args.debug else logging.INFO
    ) 
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # --- Carrega as variáveis de ambiente ---
    dotenv.load_dotenv(ENV_FILE)
    
    # Executa a função principal
    main()
