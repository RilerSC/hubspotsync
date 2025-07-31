# db/mssql_connector.py
"""
Conector para SQL Server - Gestiona la conexión y ejecución de consultas
"""
import pyodbc
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger

class MSSQLConnector:
    """Clase para gestionar conexiones y consultas a SQL Server"""
    
    def __init__(self):
        self.connection_string = settings.get_sql_connection_string()
        self.logger = get_logger('hubspot_sync.db')
        self.connection: Optional[pyodbc.Connection] = None
        
    def connect(self) -> bool:
        """
        Establece la conexión con SQL Server
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.logger.info("Estableciendo conexión con SQL Server...")
            self.connection = pyodbc.connect(self.connection_string)
            self.logger.info(f"✅ Conectado exitosamente a {settings.SQL_SERVER}/{settings.SQL_DATABASE}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error al conectar con SQL Server: {str(e)}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con SQL Server"""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("🔌 Conexión con SQL Server cerrada")
            except Exception as e:
                self.logger.error(f"Error al cerrar conexión: {str(e)}")
        
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna los resultados
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if not self.connection:
            if not self.connect():
                raise ConnectionError("No se pudo establecer conexión con SQL Server")
        
        try:
            self.logger.debug(f"Ejecutando consulta SQL...")
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Verificar si hay descripción de columnas (para SELECT statements)
            if cursor.description is None:
                # No hay resultados que retornar (INSERT, UPDATE, DELETE, etc.)
                cursor.close()
                self.logger.info("✅ Consulta ejecutada exitosamente (sin resultados)")
                return []
            
            # Obtener nombres de columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener resultados y convertir a diccionarios
            results = []
            for row in cursor.fetchall():
                result_dict = {}
                for i, value in enumerate(row):
                    # Convertir valores None a string vacío para HubSpot
                    result_dict[columns[i]] = value if value is not None else ''
                results.append(result_dict)
            
            cursor.close()
            self.logger.info(f"✅ Consulta ejecutada exitosamente. Registros obtenidos: {len(results)}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error al ejecutar consulta SQL: {str(e)}")
            raise
    
    def execute_query_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta desde un archivo SQL
        
        Args:
            file_path: Ruta al archivo SQL
            
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            self.logger.info(f"📁 Leyendo consulta desde archivo: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                query = file.read()
            
            if not query.strip():
                raise ValueError(f"El archivo {file_path} está vacío")
            
            return self.execute_query(query)
            
        except FileNotFoundError:
            self.logger.error(f"❌ Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error al leer archivo SQL {file_path}: {str(e)}")
            raise
    
    def get_insert_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene los datos para insertar en HubSpot desde la consulta HB_INSERT
        
        Returns:
            Lista de contactos para insertar
        """
        self.logger.info("🔄 Obteniendo datos para INSERT desde HB_INSERT...")
        return self.execute_query_from_file(settings.QUERY_INSERT_FILE)
    
    def get_update_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene los datos para actualizar en HubSpot desde la consulta HB_UPDATE
        
        Returns:
            Lista de contactos para actualizar
        """
        self.logger.info("🔄 Obteniendo datos para UPDATE desde HB_UPDATE...")
        return self.execute_query_from_file(settings.QUERY_UPDATE_FILE)
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a SQL Server ejecutando una consulta simple
        
        Returns:
            True si la conexión funciona correctamente
        """
        try:
            self.logger.info("🧪 Probando conexión a SQL Server...")
            result = self.execute_query("SELECT 1 as test")
            
            if result and result[0].get('test') == 1:
                self.logger.info("✅ Prueba de conexión exitosa")
                return True
            else:
                self.logger.error("❌ Prueba de conexión falló - resultado inesperado")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Prueba de conexión falló: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager - entrada"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - salida"""
        self.disconnect()
