import machine

class PIRSensor:
    """
    Driver para o sensor de presença PIR (entrada digital).
    """
    def __init__(self, pin):
        """
        Inicializa o sensor como uma entrada digital com pull-down.
        """
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
        print(f"PIR inicializado no pino {pin}.")

    def is_present(self):
        """
        Verifica se há detecção de presença.
        :return: True se detectar movimento, False caso contrário.
        """
        return bool(self.pin.value())
