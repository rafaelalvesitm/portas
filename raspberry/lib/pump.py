"""
Autor: Rafael Gomes Alves
Descrição : Esse script define uma classe para a bomba de água.
Essa classe possui os seguintes métodos:
- __init__: Inicializa a bomba com os atributos definidos no arquivo .env e no IoT Agent JSON
- __dir__: Retorna um dicionário com os atributos da bomba
- receive_commands: Método de callback para receber comandos do IoT Agent
- update_on_interval: Atualiza o intervalo de ligar a bomba
- update_off_interval: Atualiza o intervalo de desligar a bomba
- actuate: Atua a bomba ligando ou desligando
- save_data: Salva o status da bomba em um banco de dados SQLite
- send_data: Envia o status da bomba para o IoT Agent através do MQTT
- run: Loop principal que liga e desliga a bomba em intervalos regulares
"""

import random
import json
import time
import sqlite3
import logging
import os
import dotenv
import RPi.GPIO as GPIO

# from lib.mqtt_client import MqttClient


class Pump():
    def __init__(self, mqtt_client, sensor_key, sensor_id):
        """
        Descrição:
            Inicializa a bomba com os atributos definidos no arquivo .env e no IoT Agent JSON
        
        Parâmetros:
            mqtt_client: Objeto da classe MqttClient
            sensor_key: Chave do sensor definida no IoT Agent JSON
            sensor_id: ID do sensor definido no IoT Agent JSON
        """
        
        # --- Define o arquivo .env --- 
        self.dotenv_file = ".env"
        
        # --- Define os atributos do sensor ---
        self.sensor_key = sensor_key  # Chave do sensor no IoT Agent JSON
        self.sensor_id = sensor_id  # ID do sensor no IoT Agent JSON

        # --- Define os atributos da bomba ---
        self.onInterval = int(os.environ.get(f"{self.sensor_id}_onInterval", "5"))
        self.offInterval = int(os.environ.get(f"{self.sensor_id}_offInterval", "10"))
        self.status = os.environ.get(f"{self.sensor_id}_status", "off") 

        # --- Define os tópicos MQTT para enviar e receber mensagens ---
        # O tópico de envio de dados é definido no formato /json/{sensor_key}/{sensor_id}/attrs
        # O tópico de recebimento de comandos é definido no formato /{sensor_key}/{sensor_id}/cmd
        self.attrs_topic = f"/json/{self.sensor_key}/{self.sensor_id}/attrs"
        self.cmd_topic = f"/{self.sensor_key}/{self.sensor_id}/cmd"
        
        # --- Define os pinos GPIO para ligar e desligar a bomba ---
        self.pin = int(os.environ.get(f"{self.sensor_id}_PIN", "17"))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        # --- Define o cliente MQTT ---
        self.mqtt_client = mqtt_client
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(self.cmd_topic)
        self.mqtt_client.message_callback_add(self.cmd_topic, self.receive_commands)

    # --- Magic Methods ---
    def __dir__(self):
        """
        Descrição:
            Retorna um dicionário com os atributos da bomba.
            
        Retorno:
            dict: Dicionário com os atributos da bomba
        """
        return {
            "ID": self.sensor_id,
            "Intervalo ligado": self.onInterval,
            "Intervalo desligado": self.offInterval,
            "Status": self.status,
        }

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
        payload = json.loads(message.payload.decode())
        logging.info("Received command: %s", payload)

        if payload.get("setOnInterval"):
            self.update_on_interval(payload.get("setOnInterval"))
        elif payload.get("setOffInterval"):
            self.update_off_interval(payload.get("setOffInterval"))

    def update_on_interval(self, onInterval):
        """
        Descrição:
            Atualiza o intervalo de ligar a bomba.
            Atualiza o arquivo .env e envia uma mensagem para o IoT Agent.
            
        Parâmetros:
            onInterval: Intervalo de ligar a bomba em segundos
        """
        self.onInterval = onInterval
        dotenv.set_key(self.dotenv_file, f"{self.sensor_id}_onInterval", str(self.onInterval))

        logging.info("Device: {self.sensor_id} | On interval updated to {self.onInterval}")
        data = {
            "on": self.onInterval,
            "setOnInterval_info": f"Updated to {self.onInterval} seconds",
            "setOnInterval_status": "OK",
        }
        payload = json.dumps(data)
        self.mqtt_client.publish(self.attrs_topic, payload)

    def update_off_interval(self, offInterval):
        """
        Descrição:
            Atualiza o intervalo de desligar a bomba.
            Atualiza o arquivo .env e envia uma mensagem para o IoT Agent.
            
        Parâmetros:
            offInterval: Intervalo de desligar a bomba em segundos
        """
        logging.debug(
            f"Device: {self.sensor_id} | On interval updated to {self.offInterval}"
        )
        self.offInterval = offInterval
        dotenv.set_key(self.dotenv_file, f"{self.sensor_id}_offInterval", str(self.offInterval))

        data = {
            "off": self.offInterval,
            "setOffInterval_info": f"Updated to {self.offInterval} seconds",
            "setOffInterval_status": "OK",
        }
        payload = json.dumps(data)
        self.mqtt_client.publish(self.attrs_topic, payload)

    # --- Main device methods
    def actuate(self):
        """
        Descrição:
            Atua a bomba ligando ou desligando.
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Actuating {self.sensor_id}")
        if self.status == "on":
            # Turn the pump on
            GPIO.output(self.pin, GPIO.HIGH)
        elif self.status == "off":
            # Turn the pump off
            GPIO.output(self.pin, GPIO.LOW)

    def save_data(self):
        """
        Descrição:
            Salva o status da bomba em um banco de dados SQLite.
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Salvando dados no SQLITE {self.sensor_id}")
        # Create table
        try:
            conn = sqlite3.connect("./data.db")
            cur = conn.cursor()
            table_name = f"`{self.sensor_id}`"
            cur.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )"""
            )
            cur.execute(
                f"INSERT INTO {table_name} (status) VALUES (?)", (self.status,)
                )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Save to SQL | Error: {e}")

    def send_data(self):
        """
        Descrição:
            Envia o status da bomba para o IoT Agent através do MQTT.
            
        Parâmetros:
            Nenhum
        """
        logging.debug(f"Sending data to MQTT {self.sensor_id}")
        try:
            message = {
                "s": self.status, 
                "on": self.onInterval,
                "off": self.offInterval,
                "timestamp": time.time()
            }
            payload = json.dumps(message)
            self.mqtt_client.publish(self.attrs_topic, payload)
        except Exception as e:
            logging.error(f"Device: {self.sensor_id} | Send to MQTT | Error: {e}")

    # --- Loop principal ---
    def run(self):
        """
        Descrição:
            Loop principal que liga e desliga a bomba em intervalos regulares.
            
        Parâmetros:
            Nenhum
        """
        # Main loop
        while True:
            logging.info(f"Pump object: {self.__dir__()}")
            self.actuate()
            self.save_data()
            self.send_data()
            if self.status == "on":
                time.sleep(self.onInterval)
                self.status = "off"
            elif self.status == "off":
                time.sleep(self.offInterval)
                self.status = "on"