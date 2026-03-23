# Simulador de Casa Inteligente - FIWARE + ESP32

Este projeto é uma demonstração de um sistema de Casa Inteligente (Smart Home) que utiliza um microcontrolador ESP32 com MicroPython integrado à plataforma **FIWARE**. O sistema simula a coleta de dados de sensores residenciais e o controle de atuadores via comandos remotos.

## 🏠 Visão Geral

O simulador transforma o ESP32 em um hub doméstico que:
1.  **Envia dados ambientais** (Temperatura, Umidade, Luminosidade).
2.  **Monitora eventos** (Detecção de presença/movimento).
3.  **Recebe comandos** para controlar dispositivos (Lâmpada, Trava da Porta).
4.  **Recebe configurações** dinâmicas (Intervalo de leitura, Sensibilidade).

## 🚀 Tecnologias

-   **Hardware:** ESP32 (simulado ou real)
-   **Linguagem:** MicroPython
-   **Comunicação:** MQTT (JSON over MQTT)
-   **Plataforma de Contexto:** FIWARE (Orion Context Broker, IoT Agent Ultralight/JSON, Cygnus)
-   **Persistência:** MySQL & MongoDB

## 🏗️ Arquitetura

A arquitetura segue o modelo padrão FIWARE para IoT:
-   **Dispositivo (ESP32):** Atua como o `Edge`, comunicando-se via MQTT.
-   **IoT Agent (JSON):** Traduz mensagens MQTT JSON para o protocolo NGSI do Orion.
-   **Orion Context Broker:** Mantém o estado atual (Contexto) da casa inteligente.
-   **Cygnus:** Grava o histórico das leituras dos sensores no banco de dados.

## 🛠️ Sensores e Atuadores

### Sensores (Northbound)
-   **DHT22:** Temperatura (`t`) e Umidade (`h`).
-   **LDR:** Luminosidade (`l`).
-   **PIR:** Detecção de Presença (`p`).

### Atuadores (Southbound - Comandos)
-   **Lâmpada (`lamp`):** Comandos `on` / `off` acionam o **Relé**.
-   **Porta (`door`):** Comandos `lock` / `unlock` (simulado).
-   **Alarme (`bell`):** Comando `ring` (simulado).

---

## 🔌 Esquema de Conexão (Hardware Real)

Para utilizar sensores e atuadores reais, siga a pinagem configurada no `main.py`:

| Componente | Tipo | Pino ESP32 (GPIO) | Observação |
| :--- | :--- | :--- | :--- |
| **DHT22** | Digital | 23 | Sensor de Temp/Umidade |
| **LDR** | Analógico | 34 (ADC1_CH6) | Sensor de Luz |
| **PIR** | Digital | 27 | Sensor de Presença |
| **Relé** | Digital | 2 | Atuador da Lâmpada (ou LED onboard) |

---

## 🚦 Como Iniciar

### 1. Subir a Infraestrutura FIWARE
Certifique-se de ter o Docker e Docker Compose instalados.

```bash
cd platform
docker compose up -d
```

### 2. Provisionar o IoT Agent
Você precisa registrar o serviço e o dispositivo no IoT Agent para que ele saiba como traduzir as mensagens.

#### A. Registrar o Grupo de Serviços (Service Group)
Este comando define a chave de API e o tópico base MQTT.

```bash
curl -iX POST \
  'http://localhost:4041/iot/services' \
  -H 'fiware-service: smart_home' \
  -H 'fiware-servicepath: /' \
  -H 'Content-Type: application/json' \
  -d '{
 "services": [
   {
     "apikey": "house123",
     "token": "token123",
     "cbt": "http://orion:1026",
     "resource": "",
     "protocol": "PDI-IoTA-UltraLight-2.0",
     "entity_type": "SmartHouse",
     "type": "SmartHouse"
   }
 ]
}'
```

#### B. Registrar o Dispositivo (Device)
Define os atributos (sensores) e comandos (atuadores) do ESP32.

```bash
curl -iX POST \
  'http://localhost:4041/iot/devices' \
  -H 'fiware-service: smart_home' \
  -H 'fiware-servicepath: /' \
  -H 'Content-Type: application/json' \
  -d '{
 "devices": [
   {
     "device_id":   "esp32_001",
     "entity_name": "urn:ngsi-ld:SmartHouse:001",
     "entity_type": "SmartHouse",
     "protocol":    "PDI-IoTA-UltraLight-2.0",
     "transport":   "MQTT",
     "attributes": [
       { "object_id": "t", "name": "temperature", "type": "Number" },
       { "object_id": "h", "name": "humidity", "type": "Number" },
       { "object_id": "l", "name": "luminosity", "type": "Number" },
       { "object_id": "p", "name": "presence", "type": "Boolean" }
     ],
     "commands": [
       { "name": "lamp", "type": "String" },
       { "name": "door", "type": "String" },
       { "name": "bell", "type": "String" }
     ],
     "static_attributes": [
       { "name": "location", "type": "String", "value": "Living Room" }
     ]
   }
 ]
}'
```

### 3. Configurar o ESP32
1.  Edite `esp32/src/main.py` com suas credenciais de Wi-Fi.
2.  Configure o `MQTT_BROKER` com o IP da sua máquina.
3.  Carregue os arquivos para o ESP32.

---

## 📡 Testando Comandos

Para enviar um comando (ex: ligar a lâmpada) via Orion Context Broker:

```bash
curl -iX PATCH \
  'http://localhost:1026/v2/entities/urn:ngsi-ld:SmartHouse:001/attrs' \
  -H 'fiware-service: smart_home' \
  -H 'fiware-servicepath: /' \
  -H 'Content-Type: application/json' \
  -d '{
  "lamp": {
      "type": "command",
      "value": "on"
  }
}'
```

O ESP32 receberá este comando no tópico:
`/json/house123/esp32_001/cmd`

E deverá responder no tópico:
`/json/house123/esp32_001/cmdexe`
