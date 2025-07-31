# utils/logger.py
"""
Sistema de logging centralizado para el proyecto de sincronización HubSpot
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from colorama import init, Fore, Style

# Inicializar colorama para soporte de colores en Windows
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Formateador personalizado para agregar colores a los logs en consola"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

class HubSpotLogger:
    """Clase para configurar y gestionar el logging del sistema"""
    
    def __init__(self, log_dir: str = 'logs', log_level: str = 'INFO'):
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self._setup_log_directory()
        
    def _setup_log_directory(self):
        """Crea el directorio de logs si no existe"""
        self.log_dir.mkdir(exist_ok=True)
        
    def get_logger(self, name: str, include_file_handler: bool = True) -> logging.Logger:
        """
        Crea y configura un logger personalizado
        
        Args:
            name: Nombre del logger
            include_file_handler: Si incluir handler de archivo además de consola
            
        Returns:
            Logger configurado
        """
        logger = logging.getLogger(name)
        
        # Evitar duplicar handlers si ya está configurado
        if logger.handlers:
            return logger
            
        logger.setLevel(self.log_level)
        
        # Handler para consola con colores
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Formato para consola (con colores)
        console_format = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # Handler para archivo (si se solicita)
        if include_file_handler:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.log_dir / f'hubspot_sync_{today}.log'
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            
            # Formato para archivo (sin colores)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger
    
    def get_sync_logger(self) -> logging.Logger:
        """Logger específico para operaciones de sincronización"""
        return self.get_logger('hubspot_sync')
    
    def get_db_logger(self) -> logging.Logger:
        """Logger específico para operaciones de base de datos"""
        return self.get_logger('hubspot_sync.db')
    
    def get_api_logger(self) -> logging.Logger:
        """Logger específico para operaciones de API HubSpot"""
        return self.get_logger('hubspot_sync.api')

# Instancia global del sistema de logging
def setup_logging(log_dir: str = 'logs', log_level: str = 'INFO') -> HubSpotLogger:
    """
    Configura el sistema de logging global
    
    Args:
        log_dir: Directorio donde guardar los logs
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Instancia configurada de HubSpotLogger
    """
    return HubSpotLogger(log_dir=log_dir, log_level=log_level)

# Para uso directo
def get_logger(name: str) -> logging.Logger:
    """Función de conveniencia para obtener un logger"""
    logger_system = HubSpotLogger()
    return logger_system.get_logger(name)
