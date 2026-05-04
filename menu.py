import config

class EncoderMenu:
    def __init__(self, hw):
        self.hw = hw

    def update(self):
        return self.hw.has_changed()

    def selected_index(self):
        return self.hw.get_index()

    def selected_item(self):
        return config.MENU_ITEMS[self.selected_index()]

    def was_pressed(self):
        return self.hw.was_pressed()

