import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from src.config  import LOG_LEVEL

class Logger:
    
    _instances = {}
    _configured = False  # Flag para evitar reconfiguración
    
    @classmethod
    def get_logger(cls, name: str, log_file: Path = None, log_level: str = "INFO") -> logging.Logger:

        # Retornar instancia existente si ya fue creada
        if name in cls._instances:
            return cls._instances[name]
        
        # Crear nuevo logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Evitar duplicación de handlers
        if logger.handlers:
            cls._instances[name] = logger
            return logger
        
        logger.propagate = False
        
        # Handler para consola (solo INFO y superior, SIN timestamp detallado)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        # Formato simple para consola (sin duplicar timestamp)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            # Formato detallado para archivo
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Guardar instancia
        cls._instances[name] = logger
        
        return logger


def setup_logging(log_file: Path = None, log_level: str = LOG_LEVEL):

    # Configurar root logger para evitar mensajes duplicados
    root_logger = logging.getLogger()
    
    # Si ya tiene handlers, limpiarlos (evita duplicados)
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Configurar nivel del root
    root_logger.setLevel(logging.WARNING)  # Solo warnings del sistema
    
    # Retornar logger principal del proyecto
    return Logger.get_logger("pdf_processor", log_file, log_level)