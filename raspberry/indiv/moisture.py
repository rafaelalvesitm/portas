"""
Description: This script reads data from a Capacitive Soil Moisture Sensor
Author: Rafael Gomes Alves
"""


import time
import Adafruit_ADS1x15
import argparse


def main(args):
    # Create an ADS1115 ADC object
    adc = Adafruit_ADS1x15.ADS1115()

    # Set the gain to ±4.096V (adjust if needed)
    GAIN = 1

    # Main loop to read the analog value from the soil moisture sensor and print the raw ADC value
    try:
        while True:
            # Read the raw analog value from channel A3
            raw_value = adc.read_adc(3, gain=GAIN)

            # Print the raw ADC value
            print("Umidade bruta: {}".format(raw_value))

            # Add a delay between readings (adjust as needed)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSaindo do programa.")
        
    
    
if __name__ == "__main__":
    # Use arguments
    parser = argparse.ArgumentParser(description="Coleta umidade bruta do sensor de umidade")
    parser.add_argument("-t","--time", help="Tempo entre leituras", type=float, default=1 )
    args = parser.parse_args()
    
    main(args)