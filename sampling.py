from piotimer import Piotimer
from fifo import Fifo 
import config
from machine import ADC, Pin

class PulseSampler:
    def __init__(self):
        self._adc = ADC(Pin(config.ADC_PIN))
        # Increased to 500 to prevent data loss during OLED updates
        self._fifo = Fifo(500) 
        self._timer = None

    def _timer_callback(self, tid):
        """Hard interrupt: Read ADC and push to FIFO"""
        self._fifo.put(self._adc.read_u16())

    def start(self):
        """Starts the 250Hz sampling"""
        self._timer = Piotimer(mode=Piotimer.PERIODIC, freq=config.SAMPLE_RATE_HZ, callback=self._timer_callback)

    def stop(self):
        """Stops the sampling hardware timer"""
        if self._timer:
            self._timer.deinit()
            self._timer = None

    def has_sample(self): 
        """Checks if the FIFO has data available"""
        return self._fifo.has_data()
        
    def get_sample(self): 
        """Retrieves the oldest sample from the FIFO"""
        return self._fifo.get()