import paho.mqtt.client as mqtt
import json
import time
import logging

# Configura o logging para exibir informações úteis durante a execução
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class FiwareDevice:
    """
    Uma classe para representar um dispositivo se conectando à plataforma FIWARE via MQTT.
    Esta classe gerencia a conexão MQTT, a publicação de dados (atributos) e a inscrição para receber comandos.

    Nota: Antes de usar, o grupo de serviços e o dispositivo devem ser provisionados
    no FIWARE IoT Agent. Esta classe assume que o provisionamento já foi realizado.
    """

    def __init__(self, device_id, api_key, protocol="json", mqtt_broker="localhost", mqtt_port=1883):
        """
        Inicializa o FiwareDevice.

        Args:
            device_id (str): O identificador único para este dispositivo.
            api_key (str): A chave de API para o grupo de serviços provisionado.
            protocol (str): O protocolo para o IoT Agent (ex: 'json' ou 'ul'). Padrão 'json'.
            mqtt_broker (str): O endereço do broker MQTT.
            mqtt_port (int): A porta do broker MQTT.
        """
        if not all([device_id, api_key, protocol, mqtt_broker]):
            raise ValueError("device_id, api_key, protocol e mqtt_broker devem ser fornecidos.")

        self.device_id = device_id
        self.api_key = api_key
        self.protocol = protocol
        self.broker = mqtt_broker
        self.port = mqtt_port

        # Tópicos MQTT do FIWARE
        self.attrs_topic = f"/{self.protocol}/{self.api_key}/{self.device_id}/attrs"
        self.cmd_topic = f"/{self.api_key}/{self.device_id}/cmd"

        self.client = mqtt.Client(client_id=f"fiware-device-{self.device_id}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self._command_callback = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def _on_connect(self, client, userdata, flags, rc):
        """Callback para quando o cliente se conecta ao broker MQTT."""
        if rc == 0:
            self.logger.info(f"Conectado com sucesso ao broker MQTT em {self.broker}:{self.port}")
            self.logger.info(f"Inscrito no tópico de comandos: {self.cmd_topic}")
            self.client.subscribe(self.cmd_topic)
        else:
            self.logger.error(f"Falha ao conectar ao broker MQTT com código de resultado {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback para quando uma mensagem é recebida."""
        self.logger.info(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
        if msg.topic == self.cmd_topic:
            if self._command_callback:
                try:
                    payload = json.loads(msg.payload.decode())
                    self._command_callback(payload)
                except json.JSONDecodeError:
                    self.logger.error("Falha ao decodificar o JSON do payload do comando.")
            else:
                self.logger.warning("Comando recebido, mas nenhum callback está definido. Use set_command_callback().")

    def set_command_callback(self, callback):
        """
        Define a função de callback a ser executada quando um comando é recebido.

        Args:
            callback (function): A função a ser chamada. Deve aceitar um argumento: o payload do comando (dict).
        """
        self.logger.info("Callback de comando foi definido.")
        self._command_callback = callback

    def connect(self):
        """Conecta-se ao broker MQTT e inicia o loop de rede."""
        self.logger.info(f"Conectando ao broker MQTT em {self.broker}:{self.port}...")
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"Ocorreu um erro durante a conexão: {e}")

    def disconnect(self):
        """Desconecta do broker MQTT."""
        self.logger.info("Desconectando do broker MQTT.")
        self.client.loop_stop()
        self.client.disconnect()

    def send_attributes(self, data):
        """
        Envia um dicionário de atributos (medições) para o FIWARE IoT Agent.

        Args:
            data (dict): Um dicionário contendo os dados dos atributos (ex: {"temperature": 25, "humidity": 60}).
        """
        if not isinstance(data, dict):
            self.logger.error("Os dados devem ser um dicionário.")
            return

        payload = json.dumps(data)
        self.logger.info(f"Enviando atributos para {self.attrs_topic}: {payload}")
        self.client.publish(self.attrs_topic, payload)

    def send_command_result(self, command_name, result):
        """
        Envia o resultado da execução de um comando de volta para o IoT Agent.

        Args:
            command_name (str): O nome do comando que foi executado.
            result (str or dict): O resultado da execução.
        """
        result_payload = {
            f"{command_name}_info": result,
            f"{command_name}_status": "OK"
        }
        
        payload = json.dumps(result_payload)
        self.logger.info(f"Enviando resultado do comando para {self.attrs_topic}: {payload}")
        self.client.publish(self.attrs_topic, payload)


if __name__ == '__main__':
    # Exemplo de como usar a classe FiwareDevice.
    # Substitua pelos detalhes reais do seu dispositivo e broker.

    # --- Configuração ---
    DEVICE_ID = "sensor001"
    API_KEY = "4jggokgpepnvsb2uv4s40d59ov"  # Chave de API do exemplo
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883

    # --- Exemplo de Callback de Comando ---
    def handle_command(payload):
        """Função de exemplo para lidar com comandos recebidos."""
        print(f"\n--- COMANDO RECEBIDO ---")
        for command_name, value in payload.items():
            print(f"Comando: {command_name}, Valor: {value}")
            # Aqui você adicionaria a lógica para controlar um atuador
            device.send_command_result(command_name, f"Executado com valor {value}")
        print("------------------------\n")

    # --- Execução Principal ---
    print("Iniciando exemplo de dispositivo FIWARE...")

    # 1. Inicializa o dispositivo
    device = FiwareDevice(
        device_id=DEVICE_ID,
        api_key=API_KEY,
        mqtt_broker=MQTT_BROKER,
        mqtt_port=MQTT_PORT
    )

    # 2. Define a função a ser chamada quando um comando é recebido
    device.set_command_callback(handle_command)

    # 3. Conecta ao broker
    device.connect()

    # 4. Envia atributos periodicamente
    try:
        temperature = 20
        while True:
            attributes = {"t": temperature, "h": 50 + (temperature / 2)}
            device.send_attributes(attributes)
            
            temperature = (temperature + 1) % 30
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSaindo...")
    finally:
        device.disconnect()
