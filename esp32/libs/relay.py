import machine

class RelayControl:
    """
    Driver para o módulo relé (atuador digital).
    """
    def __init__(self, pin, active_low=False):
        """
        Inicializa o pino do relé como saída.
        :param active_low: Se True, o relé aciona com nível 0 (comum em módulos chineses).
        """
        self.pin = machine.Pin(pin, machine.Pin.OUT)
        self.active_low = active_low
        self.off() # Inicia desligado
        print(f"Relé inicializado no pino {pin} (active_low={active_low}).")

    def on(self):
        """
        Aciona o relé.
        """
        self.pin.value(0 if self.active_low else 1)

    def off(self):
        """
        Desliga o relé.
        """
        self.pin.value(1 if self.active_low else 0)

    def status(self):
        """
        Retorna o estado atual (ON/OFF).
        """
        val = self.pin.value()
        if self.active_low:
            return "on" if val == 0 else "off"
        return "on" if val == 1 else "off"
