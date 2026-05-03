from machine import Pin, I2C, ADC
import ssd1306
import config

class Hardware:
    def __init__(self):
        # Setup I2C for OLED
        self.i2c = I2C(1, scl=Pin(config.OLED_SCL_PIN), sda=Pin(config.OLED_SDA_PIN))
        
        # This is where your error was happening - 
        # Ensure config.OLED_WIDTH exists in config.py
        self.oled = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c)
        
        # Setup Rotary Encoder
        self.rot_a = Pin(config.ROT_A_PIN, Pin.IN, Pin.PULL_UP)
        self.rot_b = Pin(config.ROT_B_PIN, Pin.IN, Pin.PULL_UP)
        self.encoder_button = Pin(config.ENCODER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        
        # Setup LED
        self.led = Pin(config.LED_PIN, Pin.OUT)
        
        # Setup ADC for Heart Rate Sensor
        self.adc = ADC(Pin(config.ADC_PIN))