import machine

class LDRSensor:
    """
    Driver para leitura do sensor de luminosidade (LDR) usando o ADC do ESP32.
    """
    def __init__(self, pin):
        """
        Inicializa o ADC no pino especificado.
        """
        self.adc = machine.ADC(machine.Pin(pin))
        # Configura atenuação para ler até 3.6V (típico para LDR em 3.3V)
        self.adc.atten(machine.ADC.ATTN_11DB)
        print(f"LDR inicializado no pino {pin}.")

    def read_luminosity(self):
        """
        Lê o valor de luminosidade.
        :return: Valor entre 0 (escuro) e 4095 (muito claro).
        """
        try:
            return self.adc.read()
        except Exception as e:
            print(f"Erro ao ler LDR: {e}")
            return 0
