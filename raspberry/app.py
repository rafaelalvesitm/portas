import threading
import os
import logging
import sys
import argparse
import dotenv

# Importa as classes dos dispositivos e do cliente MQTT que serão utilizados
# Cada dispositivo é definido em um arquivo separado para facilitar a manutenção e a organização do código
# O cliente MQTT é definido em um arquivo separado para facilitar a reutilização do código
from lib.mqtt_client import MqttClient
from lib.dht22 import DHT22
from lib.pump import Pump
from lib.moisture import Moisture

# Variável que define o arquivo de variáveis de ambiente a ser carregado
ENV_FILE = ".env"

def main():
    """
    Descrição:
        Função principal que inicializa os dispositivos e as threads para cada um deles.
        
    Parâmetros:
        Nenhum
    """
    
    # Define as chaves de acesso dos dispositivos a serem utilizadas no IoT Agent
    # Essas chaves são definidas no arquivo .env e carregadas através da biblioteca dotenv
    DHT22_SENSOR_KEY = os.environ.get("DHT22_SENSOR_KEY")
    PUMP_ACTUATOR_KEY = os.environ.get("PUMP_ACTUATOR_KEY")
    MOISTURE_SENSOR_KEY = os.environ.get("MOISTURE_SENSOR_KEY")

    # Define os IDs dos dispositivos a serem utilizados no IoT Agent
    # Esses IDs são definidos no arquivo .env e carregados através da biblioteca dotenv
    DHT22_SENSOR_ID_1 = os.environ.get("DHT22_SENSOR_ID_1")
    PUMP_SENSOR_ID_1 = os.environ.get("PUMP_ACTUATOR_ID_1")
    MOISTURE_SENSOR_ID_1 = os.environ.get("MOISTURE_SENSOR_ID_1")

    # --- Define o cliente MQTT com suas funcionalidades ---
    # O cliente MQTT é responsável por se conectar ao IoT Agent e enviar e receber mensagens
    mqtt_client = MqttClient()

    # --- Define os dispositivos ---
    # Cada dispositivo é definido por uma classe específica de acordo com suas funcionalidades
    # e é inicializado com o cliente MQTT e as chaves e IDs de acesso
    
    # Sensor DHT22 (temperatura e umidade)
    dht22_sensor_1 = DHT22(mqtt_client, DHT22_SENSOR_KEY, DHT22_SENSOR_ID_1)

    # Atuador de bomba d'água (ou luminária, carga, etc.)
    pump_actuator_1 = Pump(mqtt_client, PUMP_ACTUATOR_KEY, PUMP_SENSOR_ID_1)

    # Sensor de umidade do solo
    Moisture_sensor_1 = Moisture(mqtt_client, MOISTURE_SENSOR_KEY, MOISTURE_SENSOR_ID_1)

    # --- Define as threads para cada dispositivo ---
    # Cada dispositivo é executado em uma thread separada para que possam funcionar de forma independente
    # e simultânea
    threads = []
    # Adiciona as threads dos dispositivos à lista de threads
    # Cada thread é criada com a função target sendo a função run do dispositivo
    # e com o daemon=True para que a thread seja finalizada quando o programa principal for finalizado	
    threads.append(threading.Thread(target=dht22_sensor_1.run, daemon=True))
    threads.append(threading.Thread(target=pump_actuator_1.run, daemon=True))
    threads.append(threading.Thread(target=Moisture_sensor_1.run, daemon=True))

    # Inicia todas as threads
    for thread in threads:
        thread.start()

    # --- Mantém a thread principal funcionando ---
    # A thread principal é mantida em execução para que o programa continue funcionando
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # Caso o usuário pressione Ctrl+C, finaliza o programa
        logging.info("Ctrl+C pressed")
        logging.info("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    # --- Defini os argumentos da linha de comando ---
    # Define o argumento -d ou --debug para habilitar o modo de debug
    parser = argparse.ArgumentParser(description="Executa sensores e atuadores")
    parser.add_argument(
        "-d", "--debug", help="Habilita o modo de debug", default=False, action="store_true"
    )

    # Faz o parse dos argumentos da linha de comando
    args = parser.parse_args()

    # --- Define o tipo de log ---
    # Define o nível de log de acordo com o modo de debug
    # Se o modo de debug estiver habilitado, o nível de log é DEBUG, caso contrário, é INFO
    log_level = (
        logging.DEBUG if args.debug else logging.INFO
    ) 
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # --- Carrega as variáveis de ambiente ---
    # Carrega as variáveis de ambiente do arquivo .env
    dotenv.load_dotenv(ENV_FILE)
    
    # Executa a função principal
    main()
