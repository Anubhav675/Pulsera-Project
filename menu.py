from machine import Pin
import config

class EncoderMenu:
    def __init__(self, pin_a, pin_b, pin_button):
        self.a = pin_a
        self.b = pin_b
        self.button = pin_button
        
        self.items = config.MENU_ITEMS
        self.index = 0
        self.last_a = self.a.value()
        
        self.pressed = False

    def update(self):
        """Returns True if the selection changed"""
        changed = False
        current_a = self.a.value()
        
        if current_a != self.last_a and current_a == 1:
            if self.b.value() != current_a:
                self.index = (self.index + 1) % len(self.items)
            else:
                self.index = (self.index - 1) % len(self.items)
            changed = True
        
        self.last_a = current_a
        return changed

    def was_pressed(self):
        """Simple debounced button check"""
        if self.button.value() == 0: # Pressed
            if not self.pressed:
                self.pressed = True
                import time
                time.sleep_ms(200) # Debounce
                return True
        else:
            self.pressed = False
        return False

    def selected_index(self):
        return self.index

    def selected_item(self):
        return self.items[self.index]