from umqtt.simple import MQTTClient
import machine
import time

class MQTTConnector:
    """
    Uma classe para gerenciar a conexão MQTT em um dispositivo ESP32.
    """
    def __init__(self, client_id, broker_address, user=None, password=None, port=0):
        """
        Inicializa o conector MQTT.
        
        :param client_id: ID único do cliente para a conexão MQTT.
        :param broker_address: Endereço do broker MQTT.
        :param user: Nome de usuário para autenticação (opcional).
        :param password: Senha para autenticação (opcional).
        :param port: Porta do broker MQTT (padrão é 1883, 0 usa o padrão).
        """
        self.client_id = client_id
        self.broker = broker_address
        self.user = user
        self.password = password
        self.port = port
        self.client = MQTTClient(self.client_id, self.broker, self.port, self.user, self.password)
        self.client.set_callback(self._default_callback)

    def _default_callback(self, topic, msg):
        """
        Callback padrão para mensagens recebidas.
        """
        print(f"Mensagem recebida do tópico '{topic.decode()}': {msg.decode()}")

    def set_callback(self, callback_func):
        """
        Define uma função de callback customizada para o recebimento de mensagens.
        
        :param callback_func: A função que será chamada quando uma mensagem for recebida.
                              Deve aceitar dois argumentos: topic e msg.
        """
        self.client.set_callback(callback_func)

    def connect(self):
        """
        Conecta ao broker MQTT. Retorna True em caso de sucesso, False caso contrário.
        """
        try:
            print(f"Conectando ao broker MQTT em '{self.broker}'...")
            self.client.connect()
            print("Conectado com sucesso ao broker MQTT.")
            return True
        except OSError as e:
            print(f"Falha ao conectar ao broker MQTT: {e}")
            self._reconnect()
            return False

    def subscribe(self, topic):
        """
        Inscreve-se em um tópico MQTT.
        
        :param topic: O tópico no qual se inscrever.
        """
        try:
            print(f"Inscrevendo-se no tópico '{topic}'...")
            self.client.subscribe(topic.encode('utf-8'))
            print("Inscrição realizada com sucesso.")
        except Exception as e:
            print(f"Falha ao se inscrever no tópico '{topic}': {e}")

    def publish(self, topic, msg, retain=False):
        """
        Publica uma mensagem em um tópico MQTT.
        
        :param topic: O tópico para o qual publicar a mensagem.
        :param msg: A mensagem a ser publicada.
        :param retain: Se a mensagem deve ser retida pelo broker.
        """
        try:
            self.client.publish(topic.encode('utf-8'), str(msg).encode('utf-8'), retain=retain)
            print(f"Mensagem '{msg}' publicada no tópico '{topic}'.")
        except Exception as e:
            print(f"Falha ao publicar no tópico '{topic}': {e}")

    def check_for_messages(self):
        """
        Verifica se há mensagens pendentes do broker. Não bloqueante.
        Deve ser chamado periodicamente em seu loop principal.
        """
        try:
            self.client.check_msg()
        except OSError as e:
            print(f"Erro ao verificar mensagens: {e}")
            self._reconnect()

    def disconnect(self):
        """
        Desconecta do broker MQTT.
        """
        self.client.disconnect()
        print("Desconectado do broker MQTT.")

    def _reconnect(self):
        """
        Tenta reconectar ao broker após uma falha.
        """
        print("Perda de conexão. Tentando reconectar em 5 segundos...")
        time.sleep(5)
        machine.reset() # A forma mais robusta de garantir a reconexão é reiniciar o dispositivo.
