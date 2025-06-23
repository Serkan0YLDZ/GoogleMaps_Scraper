from datetime import datetime
import sys
from typing import Optional

class Logger:
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self._validate_initialization()
    
    def _validate_initialization(self) -> None:
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    pass
            except (IOError, OSError) as e:
                raise RuntimeError(f"Cannot access log file {self.log_file}: {e}")
    
    def _log(self, level: str, message: str) -> None:
        if not isinstance(level, str) or not isinstance(message, str):
            raise TypeError("Level and message must be strings")
        
        if not level.strip() or not message.strip():
            raise ValueError("Level and message cannot be empty")
        
        formatted_message = f"[{level}] {message}"
        
        try:
            print(formatted_message)
            
            if self.log_file:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_formatted_message = f"[{timestamp}] [{level}] {message}"
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_formatted_message + '\n')
        except (IOError, OSError) as e:
            print(f"[ERROR] Failed to write to log file: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Unexpected logging error: {e}", file=sys.stderr)
    
    def info(self, message: str) -> None:
        self._log("INFO", message)
    
    def process(self, message: str) -> None:
        self._log("PROCESS", message)
    
    def extract(self, message: str) -> None:
        self._log("EXTRACT", message)
    
    def classify(self, message: str) -> None:
        self._log("CLASSIFY", message)
    
    def save(self, message: str) -> None:
        self._log("SAVE", message)
    
    def error(self, message: str) -> None:
        self._log("ERROR", message)
    
    def success(self, message: str) -> None:
        self._log("SUCCESS", message)
    
    def warning(self, message: str) -> None:
        self._log("WARNING", message)
    
    def debug(self, message: str) -> None:
        self._log("DEBUG", message)