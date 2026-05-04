import math
import config

class HeartRateProcessor:
    def __init__(self):
        self.reset()

    def reset(self):
        self._ppi_values = [] 
        self._sample_count = 0
        self._last_peak_sample = 0
        self._sma_buffer = []      
        self._threshold_history = [] 
        self._inside_pulse = False

    def process_sample(self, raw_sample):
        self._sample_count += 1
        beat_detected = False
        
        # Simple Moving Average for smoothing
        self._sma_buffer.append(raw_sample)
        if len(self._sma_buffer) > config.SMA_WINDOW: self._sma_buffer.pop(0)
        filtered = sum(self._sma_buffer) / len(self._sma_buffer)
        
        # Increased history for a more stable baseline
        self._threshold_history.append(filtered)
        if len(self._threshold_history) > 100: self._threshold_history.pop(0)
        avg = sum(self._threshold_history) / len(self._threshold_history)
        
        # The adaptive threshold 
        threshold = avg + config.ADAPTIVE_THRESHOLD_OFFSET 
        
        if filtered > threshold and not self._inside_pulse:
            # Calculate time since last beat in milliseconds
            time_ms = (self._sample_count - self._last_peak_sample) * 1000 / config.SAMPLE_RATE_HZ
            
            # Check against REFRACTORY_MS to prevent double-counting
            if time_ms > config.REFRACTORY_MS or self._last_peak_sample == 0:
                self._inside_pulse = True
                if self._last_peak_sample > 0 and 300 <= time_ms <= 1500:
                    self._ppi_values.append(int(time_ms))
                    beat_detected = True
                self._last_peak_sample = self._sample_count
                
        elif filtered < threshold - config.HYSTERESIS_THRESHOLD:
            self._inside_pulse = False
            
        return beat_detected, filtered

    def get_rris(self): return self._ppi_values
    def mean_ppi(self): return int(sum(self._ppi_values)/len(self._ppi_values)) if self._ppi_values else 0
    def average_bpm(self):
        m_ppi = self.mean_ppi()
        return int(60000 / m_ppi) if m_ppi > 0 else 0
        
    def sdnn(self):
        if len(self._ppi_values) < 2: return 0
        avg = sum(self._ppi_values) / len(self._ppi_values)
        var = sum((x - avg)**2 for x in self._ppi_values) / len(self._ppi_values)
        return int(math.sqrt(var))
        
    def rmssd(self):
        if len(self._ppi_values) < 2: return 0
        diffs = [(self._ppi_values[i+1] - self._ppi_values[i])**2 for i in range(len(self._ppi_values)-1)]
        return int(math.sqrt(sum(diffs) / len(diffs)))

