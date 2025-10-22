import network
import time

class WiFiConnector:
    """
    Uma classe para gerenciar a conexão WiFi em um dispositivo ESP32.
    """
    def __init__(self, ssid, password):
        """
        Inicializa o conector WiFi com o SSID e a senha da rede.
        
        :param ssid: O nome (SSID) da rede WiFi.
        :param password: A senha da rede WiFi.
        """
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        """
        Tenta conectar à rede WiFi.
        Retorna True se a conexão for bem-sucedida, False caso contrário.
        """
        if self.is_connected():
            print("Já conectado à rede.")
            print('Configuração de rede:', self.wlan.ifconfig())
            return True

        print(f"Conectando à rede '{self.ssid}'...")
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)

        # Aguarda até 10 segundos pela conexão
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print('.', end='')
            time.sleep(1)
        
        print() # Nova linha após os pontos de espera

        if self.wlan.status() != 3:
            print("Falha ao conectar ao WiFi.")
            return False
        else:
            status = self.wlan.ifconfig()
            print("Conectado com sucesso!")
            print(f"Endereço IP: {status[0]}")
            return True

    def disconnect(self):
        """
        Desconecta da rede WiFi.
        """
        if self.is_connected():
            self.wlan.disconnect()
            self.wlan.active(False)
            print("Desconectado do WiFi.")
        else:
            print("Não está conectado a nenhuma rede.")

    def is_connected(self):
        """
        Verifica se o dispositivo está conectado à rede WiFi.
        
        :return: True se estiver conectado, False caso contrário.
        """
        return self.wlan.isconnected()
