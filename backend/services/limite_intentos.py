"""
Límite de intentos fallidos de inicio de sesión (contra fuerza bruta).

Cuenta los fallos por correo y por IP en una ventana de tiempo. Vive en la
memoria del proceso: sirve con un solo proceso y se reinicia con el servidor;
con varios procesos o instancias cada una llevaría su propia cuenta (habría que
moverlo a una tabla o a Redis).
"""

import threading
import time
from collections import defaultdict, deque

MAX_FALLOS_POR_CORREO = 5
MAX_FALLOS_POR_IP = 20
VENTANA_SEGUNDOS = 15 * 60


class LimiteIntentos:
    def __init__(self, max_por_correo=MAX_FALLOS_POR_CORREO, max_por_ip=MAX_FALLOS_POR_IP, ventana=VENTANA_SEGUNDOS):
        self._max_por_correo = max_por_correo
        self._max_por_ip = max_por_ip
        self._ventana = ventana
        self._fallos: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._cerrojo = threading.Lock()

    def _recientes(self, clave: tuple[str, str], ahora: float) -> deque[float]:
        fallos = self._fallos[clave]
        while fallos and ahora - fallos[0] > self._ventana:
            fallos.popleft()
        if not fallos:
            del self._fallos[clave]
            return self._fallos[clave]
        return fallos

    def segundos_de_espera(self, correo: str, ip: str) -> int:
        """0 si puede intentar; si no, los segundos que faltan para que se libere el cupo."""
        ahora = time.monotonic()
        espera = 0.0
        with self._cerrojo:
            for clave, maximo in ((("correo", correo.strip().lower()), self._max_por_correo), (("ip", ip), self._max_por_ip)):
                fallos = self._recientes(clave, ahora)
                if len(fallos) >= maximo:
                    espera = max(espera, self._ventana - (ahora - fallos[0]))
        return int(espera) + 1 if espera > 0 else 0

    def registrar_fallo(self, correo: str, ip: str) -> None:
        ahora = time.monotonic()
        with self._cerrojo:
            self._recientes(("correo", correo.strip().lower()), ahora).append(ahora)
            self._recientes(("ip", ip), ahora).append(ahora)

    def registrar_exito(self, correo: str) -> None:
        with self._cerrojo:
            self._fallos.pop(("correo", correo.strip().lower()), None)

    def reiniciar(self) -> None:
        with self._cerrojo:
            self._fallos.clear()


limite_login = LimiteIntentos()
