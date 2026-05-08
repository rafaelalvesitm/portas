import network
import time
import json
import machine
import dht
import gc
from umqtt.simple import MQTTClient

# ==========================================
# Configurações de Rede e Broker
# ==========================================
WIFI_SSID = "CCM130"
WIFI_PASS = "fei@iot2026"
MQTT_BROKER = "192.168.137.1"
MQTT_PORT = 1883

# Configurações do FIWARE IoT Agent JSON
API_KEY = "demo"
DEVICE_ID = "urn:ngsi-ld:Estufa:001"

# Tópicos FIWARE
TOPIC_ATTRS = f"/json/{API_KEY}/{DEVICE_ID}/attrs"
TOPIC_CMD = f"/{API_KEY}/{DEVICE_ID}/cmd"
TOPIC_CMDEXE = f"/json/{API_KEY}/{DEVICE_ID}/cmdexe"

intervalo_atual = 10  # Intervalo padrão de envio em segundos

# ==========================================
# Configuração de Hardware
# ==========================================
# 1. DHT11 (Temperatura e Umidade do Ar)
sensor_dht = dht.DHT11(machine.Pin(4))

# 2. Sensor de Umidade do Solo (Analógico)
pino_solo = machine.ADC(machine.Pin(32))
pino_solo.atten(machine.ADC.ATTN_11DB)

# 3. LDR - Luz (Analógico)
pino_ldr = machine.ADC(machine.Pin(33))
pino_ldr.atten(machine.ADC.ATTN_11DB)

# 4. Módulo Relé
rele = machine.Pin(25, machine.Pin.OUT)
rele.value(0)

# 5. Servomotor (PWM)
pino_servo = machine.Pin(26)
servo = machine.PWM(pino_servo, freq=50)

def mover_servo(angulo):
    """ Converte 0-180 graus para duty cycle MicroPython (aprox 40-115) """
    angulo = max(0, min(180, angulo))
    duty = int(40 + (angulo / 180) * 75)
    servo.duty(duty)

mover_servo(0) # Inicia fechado

# ==========================================
# Funções de Conectividade e Callback
# ==========================================
def conecta_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Conectando a {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nWiFi Conectado! IP:", wlan.ifconfig()[0])

def callback_comandos(topic, msg):
    """ Processa payloads JSON recebidos no formato {"comando": valor} """
    global intervalo_atual
    
    print(f"\n[Comando Recebido] Tópico: {topic.decode()} | Payload: {msg.decode()}")
    
    try:
        payload = json.loads(msg.decode('utf-8'))
        resposta = {}

        # Comando 1: setRelay (0 ou 1)
        if "setRelay" in payload:
            estado = int(payload["setRelay"])
            rele.value(1 if estado > 0 else 0)
            resposta["setRelay"] = "OK"
            print(f"-> Relé: {'LIGADO' if estado > 0 else 'DESLIGADO'}")

        # Comando 2: setServo (0 a 180 graus)
        if "setServo" in payload:
            angulo = int(payload["setServo"])
            mover_servo(angulo)
            resposta["setServo"] = "OK"
            print(f"-> Servo: {angulo} graus")

        # Comando 3: setInterval (Segundos)
        if "setInterval" in payload:
            # Trava de segurança para não travar o loop com intervalos muito curtos
            intervalo_atual = max(2, int(payload["setInterval"]))
            resposta["setInterval"] = "OK"
            print(f"-> Novo intervalo: {intervalo_atual}s")

        # Se processamos algum comando válido, enviamos a confirmação para o tópico cmdexe
        if resposta:
            cliente_mqtt.publish(TOPIC_CMDEXE, json.dumps(resposta))
            print(f"-> Confirmação enviada: {json.dumps(resposta)}")
            
    except ValueError:
        print("Erro: O payload recebido não é um JSON válido.")
    except Exception as e:
        print(f"Erro inesperado ao processar comando: {e}")

# ==========================================
# Inicialização MQTT
# ==========================================
conecta_wifi()

print("Conectando ao Broker MQTT...")
cliente_mqtt = MQTTClient(DEVICE_ID, MQTT_BROKER, port=MQTT_PORT)
cliente_mqtt.set_callback(callback_comandos)
cliente_mqtt.connect()
cliente_mqtt.subscribe(TOPIC_CMD)
print(f"Inscrito no tópico: {TOPIC_CMD}")

# ==========================================
# Loop Principal
# ==========================================
ultimo_envio = time.ticks_ms()

try:
    while True:
        # Verifica se há novos comandos (Não bloqueante)
        cliente_mqtt.check_msg()
        
        agora = time.ticks_ms()
        if time.ticks_diff(agora, ultimo_envio) >= (intervalo_atual * 1000):
            try:
                # Leituras
                sensor_dht.measure()
                t = sensor_dht.temperature()
                h = sensor_dht.humidity()
                
                # Conversão Solo para % (4095 = seco, 0 = água total)
                solo_raw = pino_solo.read()
                solo_pct = int((1 - (solo_raw / 4095)) * 100)
                
                luz_raw = pino_ldr.read()

                # Criando o Payload JSON de Atributos
                payload_atrs = {
                    "t": t,
                    "h": h,
                    "s": solo_pct,
                    "l": luz_raw
                }
                
                # Publicando Payload JSON
                cliente_mqtt.publish(TOPIC_ATTRS, json.dumps(payload_atrs))
                print(f"Enviado: {payload_atrs}")
                
                gc.collect() # Limpeza de memória
                
            except OSError:
                print("Erro de leitura no sensor DHT11.")
            except Exception as e:
                print(f"Erro no ciclo de envio: {e}")
                
            ultimo_envio = agora
            
        time.sleep(0.1) # Pequena pausa para estabilidade do sistema

except KeyboardInterrupt:
    print("\nEncerrando...")
    cliente_mqtt.disconnect()

