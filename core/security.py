import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class BovedaSegura:
    """
    Gestiona el almacenamiento seguro (Encriptación AES) de credenciales y configuraciones.
    """
    def __init__(self):
        carpeta_madre = os.path.join(os.path.expanduser('~'), 'Documents', 'QueryLibre')
        os.makedirs(carpeta_madre, exist_ok=True)
        
        # Archivos de la bóveda
        self.ruta_boveda = os.path.join(carpeta_madre, 'vault.enc')
        self.salt_path = os.path.join(carpeta_madre, 'vault.salt')

    def boveda_existe(self) -> bool:
        """Devuelve True si ya existe una bóveda configurada en el equipo."""
        return os.path.exists(self.ruta_boveda) and os.path.exists(self.salt_path)

    def _generar_llave(self, password_maestra: str, salt: bytes) -> bytes:
        """Deriva una llave criptográfica segura a partir de la contraseña del usuario."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000, # Dificulta ataques de fuerza bruta
        )
        return base64.urlsafe_b64encode(kdf.derive(password_maestra.encode()))

    def guardar_datos(self, password_maestra: str, datos: dict):
        """Encripta un diccionario de datos y lo guarda en el disco."""
        # 1. Generamos un 'salt' aleatorio para mayor seguridad
        salt = os.urandom(16)
        with open(self.salt_path, 'wb') as f:
            f.write(salt)
        
        # 2. Creamos el candado (Fernet)
        key = self._generar_llave(password_maestra, salt)
        candado = Fernet(key)
        
        # 3. Convertimos los datos a texto y los encriptamos
        datos_str = json.dumps(datos).encode('utf-8')
        encriptado = candado.encrypt(datos_str)
        
        # 4. Guardamos el archivo cifrado
        with open(self.ruta_boveda, 'wb') as f_out:
            f_out.write(encriptado)

    def leer_datos(self, password_maestra: str) -> dict:
        """Desencripta la bóveda. Lanza ValueError si la contraseña es incorrecta."""
        if not self.boveda_existe():
            return {}
        
        # 1. Leer el salt y los datos encriptados
        with open(self.salt_path, 'rb') as f:
            salt = f.read()
            
        with open(self.ruta_boveda, 'rb') as f_in:
            encriptado = f_in.read()
            
        # 2. Reconstruir la llave
        key = self._generar_llave(password_maestra, salt)
        candado = Fernet(key)
        
        # 3. Intentar desencriptar
        try:
            desencriptado = candado.decrypt(encriptado)
            return json.loads(desencriptado.decode('utf-8'))
        except Exception:
            # Si la contraseña está mal, Fernet lanza una excepción
            raise ValueError("Contraseña maestra incorrecta o bóveda corrupta.")