"""
Autor: Rafael Gomes Alves
Descrição : Esse script define uma classe para o sensor DHT22 (temperatura e umidade).
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
import Adafruit_DHT
import RPi.GPIO as GPIO

# Importa a classe do cliente MQTT que será utilizada para enviar e receber mensagens
from lib.mqtt_client import MqttClient

# Define a classe do sensor DHT22
class DHT22():
    # Inicializa o sensor com os atributos definidos no arquivo .env e no IoT Agent JSO
    def __init__(self, mqtt_client, sensor_key, sensor_id):
        # --- Define o nome do arquivo com as variáveis de ambiente --- 
        self.dotenv_file = ".env"
        
        # --- Define os atributos (senha e ID) do sensor cadastrado no IoT Agent ---
        self.sensor_key = sensor_key  # Senha do dispositivo no IoT Agent JSON
        self.sensor_id = sensor_id  # ID do dispositivo no IoT Agent JSON

        # --- Define os atributos do sensor ---
        self.collectInterval = int(
            os.environ.get(f"{self.sensor_id}_collectInterval", "5")
        ) # Intervalo de coleta de dados em segundos
        self.temperature = None  # Dados de temperatura
        self.humidity = None  # Dados de umidade

        # --- Define os tópicos MQTT para enviar e receber mensagens ---
        # O tópico de envio de dados é definido no formato /json/{sensor_key}/{sensor_id}/attrs
        # O tópico de recebimento de comandos é definido no formato /{sensor_key}/{sensor_id}/cmd
        self.attrs_topic = f"/json/{self.sensor_key}/{self.sensor_id}/attrs"
        self.cmd_topic = f"/{self.sensor_key}/{self.sensor_id}/cmd"

        # --- Define o sensor DHT22 ---
        # O sensor DHT22 é definido com o tipo DHT22 e o pino GPIO a ser utilizado
        # Esse trecho é específico para o Raspberry Pi
        self.sensor = Adafruit_DHT.DHT22
        self.pin = int(os.environ.get(f"{self.sensor_id}_PIN", "4"))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

        # --- Define o cliente MQTT ---
        self.mqtt_client = mqtt_client
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(self.cmd_topic) # Se inscreve no tópico de comandos
        # Define o método de callback para receber comandos
        # O método receive_commands é chamado sempre que uma mensagem é recebida no tópico de comandos
        self.mqtt_client.message_callback_add(self.cmd_topic, self.receive_commands)

    def __dir__(self):
        """
        Descrição:
            Retorna um dicionário com os atributos do sensor.
        """
        return {
            "ID sensor": self.sensor_id,
            "Timestamp": time.time(),
            "Temperatura": self.temperature,
            "Umidade": self.humidity,
            "Intervalo de coleta": self.collectInterval,
        }

    # --- Método de callback do MQTT ---
    def receive_commands(self, client, userdata, message):
        """
        Descrição:
            Método de callback para receber comandos do IoT Agent.
            Esse método é chamado sempre que uma mensagem é recebida no tópico de comandos.
            
        Parâmetros:
            client: Cliente MQTT
            userdata: Dados do usuário
            message: Mensagem recebida
        """
        payload = json.loads(message.payload.decode()) # Decodifica a mensagem recebida
        logging.info("Comando recebido: %s", payload)

        # Verifica se o comando recebido é para atualizar o intervalo de coleta de dados
        if payload.get("setCollectInterval"):
            # Atualiza o intervalo de coleta de dados com o valor recebido e a função update_collect_interval
            self.update_collect_interval(payload["setCollectInterval"])

    def update_collect_interval(self, collectInterval):
        """
        Descrição:
            Atualiza o intervalo de coleta de dados do sensor.
            Esse método é chamado quando um comando é recebido para atualizar o intervalo de coleta de dados.
            
        Parâmetros:
            collectInterval: Intervalo de coleta de dados em segundos
        """
        self.collectInterval = collectInterval # Atualiza o intervalo de coleta de dados
        # Atualiza o intervalo de coleta de dados no arquivo .env
        dotenv.set_key(
            self.dotenv_file, f"{self.sensor_id}_collectInterval", str(self.collectInterval)
        )
        # Define uma mensagem para o IoT Agent informando que o intervalo de coleta de dados foi atualizado
        data = {
            "ci": self.collectInterval,
            "setCollectInterval_info": f"Updated to {self.collectInterval} seconds",
            "setCollectInterval_status": "OK",
        }
        # Define a mensagem para o tópico de envio de dados
        payload = json.dumps(data)
        # Envia a mensagem para o IoT Agent
        self.mqtt_client.publish(self.attrs_topic, payload)

    # --- Métodos para o sensor ---
    def read_data(self):
        """
        Descrição:
            Lê os dados do sensor DHT22.
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Lendo dados do sensor {self.sensor_id}")
        # Tenta ler os dados do sensor
        try:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(
                self.sensor, self.pin
            )
        # Caso ocorra um erro, exibe uma mensagem de erro
        except Exception as e:
            logging.error(f"Dispositivo: {self.sensor_id} | função read data | Erro: {e}")

    def save_data(self):
        """
        Descrição:
            Salva os dados do sensor em um banco de dados SQLite.
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Salvando dados para o SQLite{self.sensor_id}")
        # Tenta salvar os dados do sensor no banco de dados SQLite
        try:
            # Conecta ao banco de dados SQLite
            conn = sqlite3.connect("./data.db")
            cur = conn.cursor()
            table_name = f"`{self.sensor_id}`"
            cur.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL, 
                    humidity REAL
                )"""
            )
            cur.execute(
                f"INSERT INTO {table_name} (temperature, humidity) VALUES (?, ?)",
                (self.temperature, self.humidity),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Save to SQL | Error: {e}")

    def send_data(self):
        """
        Descrição:
            Envia os dados do sensor para o IoT Agent através do MQTT.	
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Enviando dados para o MQTT{self.sensor_id}")
        # Tenta enviar os dados do sensor para o IoT Agent através do MQTT
        try:
            # Verifica se os dados de temperatura e umidade são válidos
            if self.humidity is not None and self.temperature is not None:
                # Define a mensagem a ser enviada para o IoT Agent
                message = {
                    "t": self.temperature,
                    "rh": self.humidity,
                    "ci": self.collectInterval,
                    "timestamp": time.time(),
                }
                # Define a mensagem para o tópico de envio de dados
                payload = json.dumps(message)
                # Envia a mensagem para o IoT Agent
                self.mqtt_client.publish(self.attrs_topic, payload)
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Send to MQTT | Error: {e}")

    # --- Loop principal ---
    def run(self):
        """
        Descrição:
            Loop principal que lê, salva e envia os dados do sensor em intervalos regulares.
            
        Parâmetros:
            Nenhum
        """
        # Loop principal
        while True: 
            # Lê, salva e envia os dados do sensor
            self.read_data()
            self.save_data()
            self.send_data()
            logging.info(f"DHT22: {self.__dir__()}")
            time.sleep(self.collectInterval)
