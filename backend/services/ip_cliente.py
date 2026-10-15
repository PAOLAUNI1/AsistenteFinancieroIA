"""
IP del cliente para el límite de intentos de inicio de sesión.

Detrás de un proxy (Render) `request.client.host` es la IP del proxy: con ella 20 fallos de
cualquiera bloquearían a todos. El encabezado `X-Forwarded-For` trae la cadena de IP, pero solo
las entradas que añaden los proxies propios son de fiar: las anteriores las escribe el cliente.
`PROXY_HOPS` es cuántos proxies propios hay delante (Render: 1) y se toma la entrada que añadió
el más cercano al servidor, contando desde la derecha. Con 0 (por defecto) no se mira el encabezado.
"""

import os

from fastapi import Request


def _saltos_de_proxy() -> int:
    try:
        return max(int(os.getenv("PROXY_HOPS", "0")), 0)
    except ValueError:
        return 0


def ip_del_cliente(request: Request) -> str:
    saltos = _saltos_de_proxy()
    if saltos:
        entradas = [e.strip() for e in request.headers.get("x-forwarded-for", "").split(",") if e.strip()]
        if len(entradas) >= saltos:
            return entradas[-saltos]
    return request.client.host if request.client else "desconocida"
