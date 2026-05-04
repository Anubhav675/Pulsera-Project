from machine import Pin, I2C, ADC
import ssd1306
import config
import time


class Hardware:
    def __init__(self):
        # OLED
        self.i2c = I2C(1, scl=Pin(config.OLED_SCL_PIN), sda=Pin(config.OLED_SDA_PIN))
        self.oled = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c)

        # Encoder pins
        self.rot_a = Pin(config.ROT_A_PIN, Pin.IN, Pin.PULL_UP)
        self.rot_b = Pin(config.ROT_B_PIN, Pin.IN, Pin.PULL_UP)
        self.encoder_button = Pin(config.ENCODER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

        # Encoder state
        self.encoder_index = 0
        self.encoder_changed = False

        self._last_irq_time = 0
        self._debounce_ms = 5

        self._last_btn_time = 0
        self._btn_debounce = 200
        self._btn_pressed = False

        # IRQ setup
        self.rot_a.irq(trigger=Pin.IRQ_RISING, handler=self._rotary_callback)
        self.encoder_button.irq(trigger=Pin.IRQ_FALLING, handler=self._button_callback)

        # LED
        self.led = Pin(config.LED_PIN, Pin.OUT)

        # ADC
        self.adc = ADC(Pin(config.ADC_PIN))

    def _rotary_callback(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_irq_time) < self._debounce_ms:
            return

        self._last_irq_time = now

        if self.rot_b.value():
            self.encoder_index += 1
        else:
            self.encoder_index -= 1

        self.encoder_index %= len(config.MENU_ITEMS)
        self.encoder_changed = True

    def _button_callback(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_btn_time) < self._btn_debounce:
            return

        self._last_btn_time = now
        self._btn_pressed = True

    def get_index(self):
        return self.encoder_index

    def has_changed(self):
        if self.encoder_changed:
            self.encoder_changed = False
            return True
        return False

    def was_pressed(self):
        if self._btn_pressed:
            self._btn_pressed = False
            return True
        return False

