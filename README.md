# Portas Abertas FEI - Simulador IoT (Smart House)

Este projeto demonstra uma solução IoT completa utilizando **ESP32 (MicroPython)** e a plataforma **FIWARE**. Ele foi projetado para ser apresentado no evento FEI Portas Abertas.

## 🚀 Estrutura do Projeto

O sistema é dinâmico: cada ESP32 gera seu próprio **ID Único** baseado no hardware, permitindo que várias placas funcionem simultaneamente sem conflitos.

### Perfis de Demonstração:
1.  **Perfil `SIMPLE`:** Focado no sensor DHT22 (Temperatura e Umidade).
2.  **Perfil `COMPLEX`:** Inclui LDR (Luz) e Relé (Lâmpada) com automação local.

---

## 🛠️ Configuração da Plataforma (Backend)

1.  **Iniciar os serviços:**
    ```bash
    cd platform
    docker compose up -d
    ```

2.  **Configurar Autoprovisionamento:**
    Execute o script para preparar o IoT Agent para receber dados de qualquer nova placa:
    ```bash
    chmod +x provision.sh
    ./provision.sh
    ```

---

## 🔌 Configuração do Dispositivo (ESP32)

1.  **Arquivos:** Carregue `libs/` e `src/` para o ESP32.
2.  **Configuração (`src/main.py`):** 
    *   O `DEVICE_ID` será gerado automaticamente (ex: `esp32_complex_a1b2`).
    *   Ajuste `WIFI_SSID`, `WIFI_PASSWORD` e o IP do `MQTT_BROKER`.
3.  **Monitoramento:** Ao ligar a placa, verifique o console para descobrir o ID gerado pela sua ESP32.

---

## 🕹️ Interagindo com a Plataforma

Como os IDs são dinâmicos, primeiro liste as entidades para encontrar a sua:
```bash
curl -X GET "http://localhost:1026/v2/entities" \
     -H "fiware-service: smart" \
     -H "fiware-servicepath: /house"
```

### Enviar Comando (Exemplo para ID `esp32_complex_a1b2`)
Substitua o ID abaixo pelo ID único impresso no terminal da sua placa:
```bash
curl -iX PATCH \
  "http://localhost:1026/v2/entities/urn:ngsi-ld:Device:esp32_complex_a1b2/attrs" \
  -H "Content-Type: application/json" \
  -H "fiware-service: smart" \
  -H "fiware-servicepath: /house" \
  -d '{
    "lamp": {
        "type": "command",
        "value": "on"
    }
}'
```

---

## 📊 Visualização
Acesse o **Grafana** (porta 3000) e utilize o MySQL como fonte de dados para visualizar o histórico de todas as placas conectadas.
