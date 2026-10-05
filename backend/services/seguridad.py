"""
Hash y verificación de contraseñas con bcrypt. La contraseña en texto plano
nunca se guarda ni se devuelve: en `usuarios.contrasena_hash` solo queda el hash.
"""

import os

import bcrypt

# Costo del hash; los tests lo bajan con BCRYPT_ROUNDS para que no tarden.
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# bcrypt solo considera los primeros 72 bytes de la contraseña.
MAX_BYTES_CONTRASENA = 72

# Se compara contra este hash cuando el correo no existe, para que responder
# "usuario inexistente" no tarde menos que responder "contraseña incorrecta".
_HASH_FICTICIO = bcrypt.hashpw(b"contrasena-ficticia", bcrypt.gensalt(rounds=BCRYPT_ROUNDS))


def hashear_contrasena(contrasena: str) -> str:
    hash_bytes = bcrypt.hashpw(
        contrasena.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    )
    return hash_bytes.decode("utf-8")


def verificar_contrasena(contrasena: str, hash_guardado: str | None) -> bool:
    objetivo = hash_guardado.encode("utf-8") if hash_guardado else _HASH_FICTICIO
    try:
        coincide = bcrypt.checkpw(contrasena.encode("utf-8"), objetivo)
    except ValueError:
        return False
    return coincide and hash_guardado is not None
