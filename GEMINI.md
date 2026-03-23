# Gemini Instructions - Portas Project (Smart Home Simulator)

Este projeto é um Simulador de Casa Inteligente que integra um ESP32 (MicroPython) com a plataforma FIWARE via MQTT (JSON).

## Visão Geral do Projeto

O objetivo é simular um hub residencial que monitora dados ambientais e executa comandos remotos. O sistema utiliza a arquitetura FIWARE para gerenciar o contexto e persistir o histórico de dados.

### Tecnologias Principais

*   **ESP32 (MicroPython):** Coleta de dados (reais e simulados) e execução de comandos.
*   **MQTT (Mosquitto):** Protocolo de transporte para mensagens JSON.
*   **FIWARE Platform:**
    *   **Orion Context Broker:** Gerenciamento de entidades de contexto.
    *   **IoT Agent JSON:** Tradução de mensagens MQTT/JSON para NGSI.
    *   **Cygnus:** Persistência de dados em MySQL.
*   **Docker Compose:** Orquestração da infraestrutura local.

## Estrutura do Projeto

*   `/esp32`: Firmware e bibliotecas para o microcontrolador.
    *   `/libs`: Drivers para WiFi, MQTT e sensores (DHT22).
    *   `/src/main.py`: Loop principal com suporte a sensores e comandos.
*   `/platform`: Infraestrutura conteinerizada.
    *   `docker-compose.yml`: Serviços FIWARE configurados com suporte a MQTT.

## Configuração e Execução

### 1. Plataforma (Backend)

```bash
cd platform
docker compose up -d
```
O IoT Agent já está configurado no `docker-compose.yml` com `IOTA_MQTT_DISABLED=false` e apontando para o broker `mosquitto`.

### 2. Dispositivo (ESP32)

1.  Carregar `esp32/libs/` e `esp32/src/main.py` para o dispositivo.
2.  Configurar `WIFI_SSID`, `WIFI_PASSWORD` e `MQTT_BROKER` em `main.py`.

## Convenções de Desenvolvimento

*   **Linguagem:** MicroPython (ESP32) e JSON (MQTT/FIWARE).
*   **Protocolo de Mensagens:** JSON over MQTT.
*   **Tópicos MQTT:**
    *   Atributos: `/json/<API_KEY>/<DEVICE_ID>/attrs`
    *   Comandos: `/json/<API_KEY>/<DEVICE_ID>/cmd`
    *   Resposta de Comando: `/json/<API_KEY>/<DEVICE_ID>/cmdexe`
*   **Provisionamento:** O `README.md` contém os comandos `curl` necessários para registrar o Service Group e o Device no IoT Agent.

## Comandos de Verificação

*   **Logs do Sistema:** `docker compose logs -f`
*   **Simular Comando:** Usar o comando `curl` de `PATCH` descrito no `README.md` para enviar comandos ao Orion.
