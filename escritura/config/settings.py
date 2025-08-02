# config/settings.py
"""
Configuración central del sistema de sincronización HubSpot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings:
    """Configuración centralizada del sistema"""
    
    # ==================== CONFIGURACIÓN DE HUBSPOT ====================
    HUBSPOT_TOKEN: str = os.getenv('HUBSPOT_TOKEN', '')
    HUBSPOT_API_BASE_URL: str = 'https://api.hubapi.com'
    
    # ==================== CONFIGURACIÓN DE SQL SERVER ====================
    SQL_SERVER: str = os.getenv('SQL_SERVER', '')
    SQL_DATABASE: str = os.getenv('SQL_DATABASE', '')
    SQL_USER: str = os.getenv('SQL_USER', '')
    SQL_PASSWORD: str = os.getenv('SQL_PASSWORD', '')
    
    # ==================== CONFIGURACIÓN ADICIONAL ====================
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '1000'))
    SYNC_TIMEOUT: int = int(os.getenv('SYNC_TIMEOUT', '300'))
    
    # ==================== CONFIGURACIÓN DE LOGGING ====================
    LOG_LEVEL: str = 'DEBUG' if DEBUG_MODE else 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DIR: str = os.path.join(os.path.dirname(__file__), '..', 'logs')
    
    # ==================== CONSULTAS SQL ====================
    QUERY_INSERT_FILE: str = os.path.join(os.path.dirname(__file__), '..', 'HB_INSERT.sql')
    QUERY_UPDATE_FILE: str = os.path.join(os.path.dirname(__file__), '..', 'HB_UPDATE.sql')
    
    # ==================== TESTING ====================
    TEST_CEDULA: str = "107150612"  # Cédula para pruebas de un solo registro
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Valida que todas las configuraciones requeridas estén presentes"""
        required_settings = [
            ('HUBSPOT_TOKEN', cls.HUBSPOT_TOKEN),
            ('SQL_SERVER', cls.SQL_SERVER),
            ('SQL_DATABASE', cls.SQL_DATABASE),
            ('SQL_USER', cls.SQL_USER),
            ('SQL_PASSWORD', cls.SQL_PASSWORD),
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
        
        if missing_settings:
            raise ValueError(f"Configuraciones requeridas faltantes: {', '.join(missing_settings)}")
        
        return True
    
    @classmethod
    def get_sql_connection_string(cls) -> str:
        """Genera la cadena de conexión para SQL Server"""
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={cls.SQL_SERVER};"
            f"DATABASE={cls.SQL_DATABASE};"
            f"UID={cls.SQL_USER};"
            f"PWD={cls.SQL_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )

# Instancia global de configuración
settings = Settings()
