"""
Description: This script gets and prints the data for a DHT22 sensor
Author: Rafael Gomes Alves
"""

# Import needed libraries 
import sys
import Adafruit_DHT
import argparse
import time
import datetime

def main(args):
    print("Iniciando o programa")
    print(f"UUsando o pino {args.pin}")
        
    # Get the data from the sensor
    while True:
        try:
            # Get the data from the sensor
            temp, humi = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, args.pin)
            if temp is not None and humi is not None:
                print(f"Timestamp: {datetime.datetime.now()} | Temperatura: {temp:.1f}°C | Umidade: {humi:.1f}%")
        except KeyboardInterrupt:
            print(f"Saindo do programa")
            sys.exit(0)
        except Exception as e:
            print(f"Um erro aconteceu: {e}")
            sys.exit(1)
            
        time.sleep(args.time)

if __name__ == "__main__":
    # Use arguments
    parser = argparse.ArgumentParser(description="Coleta dado de umidade e temperatura do sensor DHT22")
    parser.add_argument("-p", "--pin", help="Pino da rasp no qual o sensor está conectado", type=str, default=4)
    parser.add_argument("-t","--time", help="Tempo entre leituras", type=float, default=1 )
    args = parser.parse_args()
    
    main(args)