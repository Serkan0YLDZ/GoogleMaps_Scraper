import time
import gc
from datetime import datetime

class Logger:
    def __init__(self):
        pass
    
    def _log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{level}] {message}")
    
    def info(self, message):
        self._log("INFO", message)
    
    def process(self, message):
        self._log("PROCESS", message)
    
    def extract(self, message):
        self._log("EXTRACT", message)
    
    def classify(self, message):
        self._log("CLASSIFY", message)
    
    def save(self, message):
        self._log("SAVE", message)
    
    def error(self, message):
        self._log("ERROR", message)
    
    def success(self, message):
        self._log("SUCCESS", message)