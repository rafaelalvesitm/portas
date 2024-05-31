# FEI Portas Abertas

Apresentação de um pequeno dispsoito para demonstração das funcionalidades de um sistema de Internet das Coisas. 

# Prótipo

## Hardware do dispositivo

- Raspberry Pi model 3b+ - 
- Protoboard - 
- Jumpers - Conectores macho-fêmea, macho-macho e fêmea-fêmea
- Sensor DHT22 - Sensor de umidade e temperatra do ar
- Módulo relé de 1 canal - Módulo liga-desliga para tensões 110V e 220V.
- Sensor de umidade do solo - Sensor capacitivo
- ADS1115 - Conversor Analógico-Digital

## Sistema da plataforma de Internet das Coisas

- FIWARE Orion Context Broker - Gerenciador de contexto
- FIWARE IoT Agent JSON - Tradutor de protocolos
- Mosquitto MQTT Broker - Gestor de mensagens MQTT
- FIWARE Cygnus - Componente para persisir dados em bancos de dados relacionais
- Banco de dados Mongodb - Banco de dados não relacional
- Banco de dados MySQL - Banco de dados relacional
- Grafana - Criador de painéis personalizados