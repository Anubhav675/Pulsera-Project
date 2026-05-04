import config

class EncoderMenu:
    def __init__(self, hardware):
        self.hw = hardware
        self.items = config.MENU_ITEMS

    def update(self):
        return self.hw.has_changed()

    def was_pressed(self):
        return self.hw.was_pressed()

    def selected_index(self):
        return self.hw.get_index()

    def selected_item(self):
        return self.items[self.hw.get_index()]