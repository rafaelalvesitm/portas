
# FIWARE IoT Platform: Monitoramento de Estufa Inteligente

Este repositório contém a infraestrutura completa para uma plataforma de Internet das Coisas (IoT) baseada no ecossistema FIWARE, integrada com um dispositivo ESP32 para monitoramento e controle de uma estufa inteligente.

---

## 1. Arquitetura da Plataforma

A solução utiliza o framework FIWARE para gestão de dados de contexto em tempo real, permitindo escalabilidade e integração padronizada.

| Camada | Componente | Descrição Técnica |
| --- | --- | --- |
| **Context Management** | Orion Context Broker | Núcleo do sistema. Gerencia o estado atual das entidades via API NGSI v2. |
| **Persistência** | MongoDB | Banco NoSQL para armazenamento de registros e metadados do Orion e IoT Agent. |
| **Southbound (IoT)** | IoT Agent JSON | Traduz mensagens MQTT/JSON para o formato NGSI v2 do Orion. |
| **Protocolo de Campo** | Eclipse Mosquitto | Broker MQTT que intermedia a comunicação entre o ESP32 e a plataforma. |
| **Northbound (Histórico)** | Cygnus | Persiste mudanças de contexto do Orion em bancos de dados relacionais. |
| **Série Temporal** | MySQL 8.0 | Armazenamento histórico de longo prazo para análise de tendências. |
| **Visualização** | Grafana | Dashboards interativos para monitoramento visual dos dados coletados. |

---

## 2. Hardware: Sensores e Atuadores

O projeto utiliza um **ESP32** executando MicroPython para interagir com o ambiente físico.

### Sensores (Entrada de Dados)
| Grandeza | Sensor | Pino (ESP32) | Atributo FIWARE | Atributo JSON |
| --- | --- | --- | --- | --- |
| Temperatura | DHT11 | GPIO 4 | `temperatura` | `t` |
| Umidade do Ar | DHT11 | GPIO 4 | `umidade` | `h` |
| Umidade do Solo | Higrômetro (Analógico) | GPIO 32 | `umidadeSolo` | `s` |
| Luminosidade | LDR (Analógico) | GPIO 33 | `luminosidade` | `l` |

### Atuadores (Comandos)
| Dispositivo | Função | Pino (ESP32) | Comando FIWARE |
| --- | --- | --- | --- |
| Relé | Controle de bomba/lâmpada | GPIO 25 | `setRelay` (0 ou 1) |
| Servomotor | Controle de abertura/janela | GPIO 26 | `setServo` (0 a 180) |
| Sistema | Intervalo de atualização | - | `setInterval` (segundos) |

---

## 3. Funcionalidades e Fluxo de Dados

1. **Monitoramento**: O ESP32 realiza a leitura dos sensores e envia um JSON via MQTT para o tópico `/json/demo/urn:ngsi-ld:Estufa:001/attrs`.
2. **Processamento**: O IoT Agent converte este JSON em atributos no Orion Context Broker.
3. **Persistência**: O Cygnus detecta mudanças no Orion e salva os dados no MySQL.
4. **Controle**: Comandos enviados via Orion (PATCH) são encaminhados pelo IoT Agent para o tópico MQTT `/demo/urn:ngsi-ld:Estufa:001/cmd`. O ESP32 processa e confirma a execução no tópico `cmdexe`.

---

## 4. Como Executar o Projeto

### Passo 1: Subir a Infraestrutura
Certifique-se de ter o Docker instalado. Na raiz do projeto, execute:
```bash
docker compose -f platform/docker-compose.yml up -d
```

### Passo 2: Configurar o Dispositivo (ESP32)
1. Certifique-se de ter o MicroPython instalado no ESP32.
2. Edite o arquivo `esp32/main.py` com as credenciais do seu WiFi (`WIFI_SSID` e `WIFI_PASS`) e o IP do seu computador (`MQTT_BROKER`) onde o Docker está rodando.
3. Envie o arquivo para o ESP32.

### Passo 3: Provisionamento e Testes (Postman)
Utilize o arquivo `Portas.postman_collection` no Postman para realizar as requisições na ordem correta:
1. **IoT Agent - Cria um grupo**: Define a API Key (`demo`) e o protocolo.
2. **IoT Agent - Providenciando a Estufa**: Registra o dispositivo `urn:ngsi-ld:Estufa:001` e mapeia sensores/comandos.
3. **Subscrições geral**: Configura o Orion para enviar notificações ao Cygnus.
4. **Orion - Verifica a estufa**: Valida se os dados do ESP32 estão sendo refletidos no Orion.
5. **Comandos (Ex: Acionando servo)**: Testa o controle remoto do hardware.

---

## 5. Visualização no Grafana

Acesse `http://localhost:3000` (admin/admin).
Para configurar o dashboard, adicione o MySQL (`mysql-db:3306`) como fonte de dados.

**Query de exemplo para Temperatura:**
```sql
SELECT
  CAST(recvTime AS DATETIME(3)) AS "time",
  CAST(attrValue AS DOUBLE) AS "Temperatura"
FROM
  openiot.`urn_ngsi-ld_Estufa_001_Estufa`
WHERE
  attrName = 'temperatura' AND
  $__timeFilter(CAST(recvTime AS DATETIME(3)))
ORDER BY 1
```

---

## 6. Requisições Disponíveis (Resumo)

| Ação | Endpoint | Descrição |
| --- | --- | --- |
| Health Check | `GET /version` ou `/iot/about` | Verifica se os serviços estão online. |
| Provisionamento | `POST /iot/services` | Registra a API Key (`demo`). |
| Registro | `POST /iot/devices` | Registra a entidade `urn:ngsi-ld:Estufa:001`. |
| Comandos | `PATCH /v2/entities/.../attrs` | Envia comandos (`setRelay`, `setServo`, `setInterval`). |
| Histórico | `GET /v2/subscriptions` | Verifica as regras de persistência. |
