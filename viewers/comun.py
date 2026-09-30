import glob
import html
import os
import re
import sys


def encontrar_xml(ruta=None):
    """Devuelve la ruta del XML a usar.

    Si se pasa una ruta, se usa esa. Si no, se busca un .xml en la carpeta del
    proyecto; si hay más de uno, se le pregunta al usuario cuál abrir.
    """
    if ruta:
        if not os.path.isfile(ruta):
            print(f"No existe el archivo '{ruta}'.")
            sys.exit(1)
        return ruta

    base = os.path.dirname(os.path.abspath(__file__))
    raiz = os.path.dirname(base)
    candidatos = sorted(glob.glob(os.path.join(raiz, "*.xml")) + glob.glob(os.path.join(base, "*.xml")))

    if not candidatos:
        print("No se encontró ningún archivo .xml en el proyecto.")
        print("Pasá la ruta como parámetro: py main.py tu_proyecto.xml")
        sys.exit(1)

    if len(candidatos) == 1:
        return candidatos[0]

    print("Se encontraron varios archivos .xml:")
    for i, candidato in enumerate(candidatos, start=1):
        print(f"{i}. {os.path.basename(candidato)}")

    while True:
        entrada = input("¿Cuál querés abrir? ").strip()
        if entrada.isdigit() and 1 <= int(entrada) <= len(candidatos):
            return candidatos[int(entrada) - 1]
        print("Opción inválida.")


def leer_xml(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def bloques_device(contenido):
    return [m.group(0) for m in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL)]


def texto(bloque, tag):
    m = re.search(rf"<{tag}>([^<]*)</{tag}>", bloque)
    return m.group(1) if m and m.group(1) else None


def atributos_extendidos(bloque):
    crudo = texto(bloque, "EXT_ATTRIBUTES")
    if not crudo:
        return {}

    atributos = {}
    for par in crudo.split(";"):
        if ":" in par:
            clave, valor = par.split(":", 1)
            if clave.strip():
                atributos[clave.strip()] = valor.strip()
    return atributos


def decodificar(valor):
    """Convierte las entidades del XML (&lt; &gt; &amp;...) en sus caracteres.

    Recorre diccionarios, listas y tuplas, así se aplica una sola vez sobre
    todo lo que devuelve un parser.
    """
    if isinstance(valor, str):
        return html.unescape(valor)
    if isinstance(valor, dict):
        return {decodificar(k): decodificar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [decodificar(v) for v in valor]
    if isinstance(valor, tuple):
        return tuple(decodificar(v) for v in valor)
    return valor


def agregar_dispositivo(dispositivos, nombre, datos):
    """Agrega un dispositivo sin pisar a otro que tenga el mismo nombre.

    Si el nombre ya existe, se guarda como "Nombre (2)", "Nombre (3)", etc.
    """
    clave = nombre
    numero = 2
    while clave in dispositivos:
        clave = f"{nombre} ({numero})"
        numero += 1
    dispositivos[clave] = datos
