import framebuf
import config
import my_icon

class Display:
    def __init__(self, oled):
        self._oled = oled
        self.width = config.OLED_WIDTH
        self.height = config.OLED_HEIGHT
        self._wave_history = [config.OLED_HEIGHT // 2] * 128 

    def show_splash(self):
        self._oled.fill(0)
        try:
            icon_buf = framebuf.FrameBuffer(my_icon.img, 128, 64, framebuf.MONO_VLSB)
            self._oled.blit(icon_buf, 0, 0) 
        except Exception as e:
            self._oled.text("HRV-MOD", 25, 30, 1)
        self._oled.show()

    def show_menu(self, items, selected_idx):
        self._oled.fill(0)
        self._oled.text(" PULSERA ", 15, 0, 1)
        self._oled.hline(0, 10, 128, 1)
        for i, item in enumerate(items):
            y = 15 + (i * 12)
            prefix = ">" if i == selected_idx else " "
            self._oled.text(f"{prefix} {item}", 0, y, 1)
        self._oled.show()

    def draw_ppg_wave(self, bpm, raw_val):
        """Live PPG Signal (Level 4 Requirement)"""
        try:
            self._wave_history.append(raw_val)
            self._wave_history.pop(0)
            
            l_min, l_max = min(self._wave_history), max(self._wave_history)
            d_range = l_max - l_min
            
            
            if d_range < config.NOISE_FLOOR_RANGE or d_range == 0: 
                d_range = 4000
                l_min = raw_val - 2000
            
            self._oled.fill(0)
            self._oled.text(f"BPM: {bpm}", 0, 0, 1)
            
            
            for i in range(len(self._wave_history) - 1):
                y1 = 63 - int((self._wave_history[i] - l_min) * 40 / d_range)
                y2 = 63 - int((self._wave_history[i+1] - l_min) * 40 / d_range)
                self._oled.line(i, y1, i+1, y2, 1)
            
            self._oled.show()
        except:
            pass 

    def show_collecting(self, time_val, mode):
        self._oled.fill(0)
        self._oled.text(f"MODE: {mode}", 0, 0, 1)
        self._oled.text(f"Time: {time_val}s", 0, 25, 1)
        progress = min(time_val if mode == "Kubios" else (30 - time_val), 30) / 30
        self._oled.rect(5, 50, 118, 10, 1)
        self._oled.fill_rect(5, 50, int(progress * 118), 10, 1)
        self._oled.show()

    def show_hrv_results(self, bpm, ppi, rmssd, sdnn):
        self._oled.fill(0)
        self._oled.text("HRV RESULTS", 20, 0, 1)
        self._oled.hline(0, 10, 128, 1)
        self._oled.text(f"HR:   {int(bpm)} bpm", 0, 16, 1)
        self._oled.text(f"PPI:  {int(ppi)} ms", 0, 28, 1)
        self._oled.text(f"RMSSD:{int(rmssd)} ms", 0, 40, 1)
        self._oled.text(f"SDNN: {int(sdnn)} ms", 0, 52, 1)
        self._oled.show()

    def show_kubios_results(self, hr, rmssd, sdnn, pns, sns):
        self._oled.fill(0)
        self._oled.text("KUBIOS READY", 15, 0, 1)
        self._oled.text(f"HR: {int(hr)} RM:{int(rmssd)}", 0, 18, 1)
        self._oled.text(f"PNS:{pns:.1f} SNS:{sns:.1f}", 0, 32, 1)
        self._oled.text("PRESS TO MENU", 10, 52, 1)
        self._oled.show()

    def show_history_list(self, history, selected_idx):
        self._oled.fill(0)
        self._oled.text("HISTORY", 35, 0, 1)
        if selected_idx == 0:
            self._oled.fill_rect(0, 12, 128, 11, 1)
            self._oled.text("<-- BACK", 5, 14, 0)
        else:
            self._oled.text("<-- BACK", 5, 14, 1)
        for i in range(3):
            r_idx = i + (max(1, selected_idx) - 1)
            if r_idx >= len(history): break
            y = 28 + (i * 12)
            pre = ">" if (r_idx + 1) == selected_idx else " "
            self._oled.text(f"{pre}Rec {r_idx+1}:{history[r_idx]['bpm']}BPM", 0, y, 1)
        self._oled.show()

    def show_history_detail(self, entry, idx, total):
        self._oled.fill(0)
        self._oled.text(f"REC {idx+1}/{total}", 0, 0, 1)
        self._oled.text(f"HR: {entry['bpm']}", 0, 16, 1)
        self._oled.text(f"RMSSD: {entry['rmssd']}ms", 0, 28, 1)
        self._oled.text(f"SDNN: {entry['sdnn']}ms", 0, 40, 1)
        self._oled.text("PRESS TO EXIT", 10, 52, 1)
        self._oled.show()

    def show_message(self, text):
        self._oled.fill(0)
        self._oled.text(text, (self.width - len(text)*8)//2, 30, 1)
        self._oled.show()
