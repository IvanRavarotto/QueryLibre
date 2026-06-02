import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

LOGGER = logging.getLogger("QueryLibre")

class MotorBaseDatos:
    """
    Clase base para la conexión a bases de datos (SQLite, PostgreSQL, MySQL).
    Actúa como puente arquitectónico para futuras integraciones.
    """
    def __init__(self):
        self.engine = None
        self.conexion_activa = False

    def conectar(self, uri_conexion):
        """Establece y verifica la conexión a la base de datos."""
        try:
            # create_engine maneja el pool de conexiones automáticamente
            self.engine = create_engine(uri_conexion)
            
            # Un 'ping' rápido para confirmar que las credenciales son válidas
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.conexion_activa = True
            LOGGER.info("Conexión a la base de datos establecida con éxito.")
            return True
            
        except SQLAlchemyError as e:
            self.conexion_activa = False
            LOGGER.error(f"Error al conectar a la base de datos: {e}")
            return False

    def desconectar(self):
        """Libera los recursos y cierra el pool de conexiones."""
        if self.engine:
            self.engine.dispose()
            self.conexion_activa = False
            LOGGER.info("Conexión a la base de datos cerrada de forma segura.")