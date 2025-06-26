import numpy as np
import time
from scipy.signal import find_peaks

class SoundDetector:
    def __init__(self, samplerate=16000, blocksize=1024, debounce_time=0.8):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.last_sound_time = {}
        self.debounce_time = debounce_time
        self.prev_block = np.zeros(blocksize)

    def _debounce(self, sound):
        now = time.time()
        last_time = self.last_sound_time.get(sound, 0)
        if now - last_time > self.debounce_time:
            self.last_sound_time[sound] = now
            return True
        return False

    def detect(self, audio_block):
        # Normalize
        audio = audio_block / np.max(np.abs(audio_block) + 1e-6)
        # --- Detect Clap Sound (short, high amplitude) ---
        if np.max(np.abs(audio)) > 0.7:
            # Check for short burst
            if np.mean(np.abs(audio)) < 0.2:
                if self._debounce('clap_sound'):
                    return 'clap_sound'
        # --- Detect Snap (short, sharp frequency burst) ---
        fft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/self.samplerate)
        if np.max(fft) > 20 and np.argmax(fft) > 1000:
            if self._debounce('snap'):
                return 'snap'
        # --- Detect Humming (sustained low pitch, 100-200 Hz) ---
        # Use autocorrelation for pitch detection
        corr = np.correlate(audio, audio, mode='full')
        corr = corr[len(corr)//2:]
        d = np.diff(corr)
        start = np.where(d > 0)[0][0]
        peak = np.argmax(corr[start:]) + start
        if peak > 0:
            freq = self.samplerate / peak
            if 100 < freq < 200 and np.mean(np.abs(audio)) > 0.1:
                if self._debounce('humming'):
                    return 'humming'
        return None 