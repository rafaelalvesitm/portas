"""
Description: This script turns a lamp on and off
Author: Rafael Gomes Alves
"""

# Import needed libraries 
import sys
import Adafruit_DHT
import argparse
import time
import datetime
import RPi.GPIO as GPIO

def main(args):
    print("Iniciando o programa")
    print(f"Usando o pino {args.pin}")
        
    # Define a lampada como um relé
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(args.pin, GPIO.OUT)

    while True:
        try:
            # Muda o estado da lampada
            if GPIO.input(args.pin):
                print(f"Desligando a bomba")
                GPIO.output(args.pin, GPIO.LOW)
            else:
                print(f"Ligando a bomba")
                GPIO.output(args.pin, GPIO.HIGH)
            
            # Espera um tempo
            time.sleep(args.time)
            
        except KeyboardInterrupt:
            print("Fechando o programa")
            break
        except Exception as e:
            print(f"Um erro ocorreu: {e}")
            break
            
            
if __name__ == "__main__":
    # Use arguments
    parser = argparse.ArgumentParser(description="TLiga e desliga a bomba")
    parser.add_argument("-p", "--pin", help="Pino da Rasp em que a bomba está conectada", type=str, default=17)
    parser.add_argument("-t","--time", help="Tempo entre ligar e desligar a bomba", type=float, default=1 )
    args = parser.parse_args()
    
    main(args)