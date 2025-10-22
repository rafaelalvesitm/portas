import machine
import dht
import time

# Define o pino ao qual o pino de dados do DHT22 está conectado
# Para o ESP32, você pode usar qualquer pino GPIO. Vamos usar o GPIO 4 (D4).
dht_pin = machine.Pin(23)

# Cria um objeto do sensor DHT22
sensor = dht.DHT22(dht_pin)

print("Lendo o sensor DHT22...")

while True:
    try:
        # Mede a temperatura e a umidade
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        # Imprime as leituras
        print(f"Temperatura: {temp:.2f} | Umidade: {hum:.2f}%")

    except OSError as e:
        print("Falha ao ler o sensor.")
        
    # Aguarda 2 segundos antes da próxima leitura
    time.sleep(2)

