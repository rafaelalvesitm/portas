"""
Autor: Rafael Gomes Alves
Descrição : Esse script define uma classe para o sensor de umidade do solo.
Essa classe possui os seguintes métodos:
- __init__: Inicializa o sensor com os atributos definidos no arquivo .env e no IoT Agent JSON
- __dir__: Retorna um dicionário com os atributos do sensor
- receive_commands: Método de callback para receber comandos do IoT Agent
- update_collect_interval: Atualiza o intervalo de coleta de dados do sensor
- read_data: Lê os dados do sensor
- save_data: Salva os dados do sensor em um banco de dados SQLite
- send_data: Envia os dados do sensor para o IoT Agent através do MQTT
- run: Loop principal que lê, salva e envia os dados do sensor em intervalos regulares
"""

import random
import json
import time
import sqlite3
import logging
import os
import dotenv
import Adafruit_ADS1x15
import RPi.GPIO as GPIO

# Importa a classe do cliente MQTT que será utilizada para enviar e receber mensagens
from lib.mqtt_client import MqttClient

class Moisture():
    # Inicializa o sensor com os atributos definidos no arquivo .env e no IoT Agent JSON
    def __init__(self, mqtt_client, sensor_key, sensor_id):
        """
        Descrição:
            Inicializa o sensor de umidade do solo com os atributos definidos no arquivo .env e no IoT Agent JSON
        
        Parâmetros:
            mqtt_client: Cliente MQTT para enviar e receber mensagens
            sensor_key: Chave do sensor cadastrada no IoT Agent JSON
            sensor_id: ID do sensor cadastrado no IoT Agent JSON
        """
        # --- Define o arquivo com as variáveis de ambiente --- 
        self.dotenv_file = ".env"
        
        # --- Define os atributos do sensor ---
        self.sensor_key = sensor_key  # Chave do sensor no IoT Agent JSON
        self.sensor_id = sensor_id  # ID do sensor no IoT Agent JSON
        self.collectInterval = int(
            os.environ.get(f"{self.sensor_id}_collectInterval", "5")
        ) # Intervalo de coleta de dados em segundos
        self.moisture = None  # Dados de umidade do solo

        # --- Define os tópicos MQTT para enviar e receber mensagens ---
        # O tópico de envio de dados é definido no formato /json/{sensor_key}/{sensor_id}/attrs
        # O tópico de recebimento de comandos é definido no formato /{sensor_key}/{sensor_id}/cmd
        self.attrs_topic = f"/json/{self.sensor_key}/{self.sensor_id}/attrs"
        self.cmd_topic = f"/{self.sensor_key}/{self.sensor_id}/cmd"

        # --- Define o sensor de umidade do solo ---
        # O sensor de umidade do solo é definido com o ADS1115 e o pino GPIO a ser utilizado
        self.sensor = Adafruit_ADS1x15.ADS1115()
        # Define o ganho do sensor (1, 2/3, 1, 2, 4, 8, 16)
        self.GAIN = os.environ.get(f"{self.sensor_id}_GAIN", "1")
        self.PIN = os.environ.get(f"{self.sensor_id}_PIN", "3")

        # --- Define o cliente MQTT ---
        self.mqtt_client = mqtt_client
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(self.cmd_topic)
        self.mqtt_client.message_callback_add(self.cmd_topic, self.receive_commands)

    def __dir__(self):
        """
        Descrição:
            Retorna um dicionário com os atributos do sensor.
            
        Parâmetros:
            Nenhum
        """
        
        return {
            "ID do sensor": self.sensor_id,
            "Timestamp": time.time(),
            "Umidade": self.moisture,
            "Tempo de coleta": self.collectInterval,
        }

    # --- Método de callback do MQTT ---
    def receive_commands(self, client, userdata, message):
        """
        Descrição:
            Método de callback para receber comandos do IoT Agent
            
        Parâmetros:
            client: Cliente MQTT
            userdata: Dados do usuário
            message: Mensagem recebida do IoT Agent
        """
        payload = json.loads(message.payload.decode())
        logging.info("Received command: %s", payload)

        # Verifica se o comando recebido é para atualizar o intervalo de coleta
        if payload.get("setCollectInterval"):
            self.update_collect_interval(payload["setCollectInterval"])

    def update_collect_interval(self, collectInterval):
        """
        Descrição:
            Atualiza o intervalo de coleta de dados do sensor
            
        Parâmetros:
            collectInterval: Novo intervalo de coleta de dados em segundos
        """
        # Atualiza o intervalo de coleta de dados e salva no arquivo .env
        self.collectInterval = collectInterval
        dotenv.set_key(
            self.dotenv_file, f"{self.sensor_id}_collectInterval", str(self.collectInterval)
        )
        # Envia a confirmação do comando para o IoT Agent
        data = {
            "ci": self.collectInterval,
            "setCollectInterval_info": f"Updated to {self.collectInterval} seconds",
            "setCollectInterval_status": "OK",
        }
        payload = json.dumps(data) # Converte o dicionário para JSON
        # Envia a mensagem para o IoT Agent
        self.mqtt_client.publish(self.attrs_topic, payload)

    # --- Funções do sensor ---
    def read_data(self):
        """
        Desrição:
            Lê os dados do sensor de umidade do solo
            
        Parâmetros: 
            Nenhum
        """
        logging.debug(f"Lendo dados do sensor {self.sensor_id}")
        # Lê os dados do sensor de umidade do solo
        try:
            self.moisture = self.sensor.read_adc(int(self.PIN), gain=int(self.GAIN))
        except Exception as e:
            logging.error(f"Dispositivo: {self.sensor_id} | Função read data | Erro: {e}")

    def save_data(self):
        """
        Descrição:
            Salva os dados do sensor de umidade do solo em um banco de dados SQLite
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Salvando dados do sensor {self.sensor_id}")
        # Salva os dados do sensor de umidade do solo em um banco de dados SQLite
        try:
            conn = sqlite3.connect("./data.db")
            cur = conn.cursor()
            table_name = f"`{self.sensor_id}`"
            cur.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    moisture REAL
                )"""
            )
            cur.execute(
                f"INSERT INTO {table_name} (moisture) VALUES (?)",
                (int(self.moisture),),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Save to SQL | Error: {e}")

    def send_data(self):
        """
        Descrição:
            Envia os dados do sensor de umidade do solo para o IoT Agent através do MQTT
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Sending data to MQTT {self.sensor_id}")
        try:
            if self.moisture is not None:
                message = {
                    "m": self.moisture,
                    "ci": self.collectInterval,
                    "timestamp": time.time(),
                }
                payload = json.dumps(message)
                self.mqtt_client.publish(self.attrs_topic, payload)
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Send to MQTT | Error: {e}")

    # --- Loop principal ---
    def run(self):
        # Loop principal que lê, salva e envia os dados do sensor em intervalos regulares
        while True:
            self.read_data()
            self.save_data()
            self.send_data()
            logging.info(f"Sensor umidade do solo: {self.__dir__()}")
            time.sleep(self.collectInterval)
