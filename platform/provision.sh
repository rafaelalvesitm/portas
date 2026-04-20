#!/bin/bash

# Configurações do IoT Agent
IOTA_HOST="localhost"
IOTA_PORT=4041
API_KEY="feiportas"

echo "### Provisionando FIWARE para o evento FEI Portas Abertas ###"
echo "### Modo: Autoprovisionamento (Dinâmico) ###"

# 1. Provisionar Grupo de Serviço
# O autoprovisionamento permite que novos dispositivos sejam criados automaticamente
# assim que enviarem a primeira mensagem MQTT com a API_KEY correta.
echo -e "\n1. Criando Grupo de Serviço (com suporte a Comandos)..."
curl -iX POST "http://$IOTA_HOST:$IOTA_PORT/iot/services" \
     -H "Content-Type: application/json" \
     -H "fiware-service: smart" \
     -H "fiware-servicepath: /house" \
     -d '{
 "services": [
   {
     "apikey": "'$API_KEY'",
     "cbtype": "Thing",
     "resource": "/json",
     "entity_type": "SmartDevice",
     "attributes": [
        { "object_id": "t", "name": "temperature", "type": "Float" },
        { "object_id": "h", "name": "humidity", "type": "Float" },
        { "object_id": "l", "name": "luminosity", "type": "Integer" }
     ],
     "commands": [
        { "name": "lamp", "type": "command" },
        { "name": "auto", "type": "command" }
     ]
   }
 ]
}'

echo -e "\n\n### Grupo de Serviço configurado! ###"
echo "Agora qualquer ESP32 que enviar dados com a API_KEY '$API_KEY' será registrada automaticamente."
