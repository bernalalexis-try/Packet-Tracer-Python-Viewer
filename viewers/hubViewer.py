import glob
import os
import re
import sys

TIPO = "Hub"


def encontrar_xml():
    base = os.path.dirname(os.path.abspath(__file__))
    raiz = os.path.dirname(base)
    candidatos = glob.glob(os.path.join(raiz, "*.xml")) + glob.glob(os.path.join(base, "*.xml"))
    if not candidatos:
        print("No se encontró ningún archivo .xml en el proyecto.")
        sys.exit(1)
    return candidatos[0]


def _texto(bloque, tag):
    m = re.search(rf"<{tag}>([^<]*)</{tag}>", bloque)
    return m.group(1) if m and m.group(1) else None


def parsear_atributos_extendidos(bloque):
    crudo = _texto(bloque, "EXT_ATTRIBUTES")
    if not crudo:
        return {}

    atributos = {}
    for par in crudo.split(";"):
        if ":" in par:
            clave, valor = par.split(":", 1)
            if clave.strip():
                atributos[clave.strip()] = valor.strip()
    return atributos


def parsear_dispositivos(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    dispositivos = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != TIPO:
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else TIPO

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        rc_match = re.search(r"<RUNNINGCONFIG>(.*?)</RUNNINGCONFIG>", bloque, re.DOTALL)
        lineas_config = re.findall(r"<LINE>(.*?)</LINE>", rc_match.group(1)) if rc_match else []

        dispositivos[nombre] = {
            "modelo": modelo,
            "serial": serial,
            "encendido": _texto(bloque, "POWER") == "true",
            "macs": re.findall(r"<MACADDRESS>([^<]*)</MACADDRESS>", bloque),
            "atributos": parsear_atributos_extendidos(bloque),
            "lineas_config": lineas_config,
        }

    return dispositivos


def mostrar_identidad(nombre, datos):
    print(f"Nombre       : {nombre}")
    print(f"Tipo         : Hub")
    print(f"Modelo       : {datos['modelo']}")
    print(f"Numero serie : {datos['serial']}")
    print(f"Encendido    : {'si' if datos['encendido'] else 'no'}")


def mostrar_puertos(datos):
    if not datos["macs"]:
        print("Sin puertos con MAC registrada.")
        return

    for i, mac in enumerate(datos["macs"], start=1):
        print(f"  Puerto {i}: MAC {mac}")


def mostrar_atributos(datos):
    if not datos["atributos"]:
        print("Sin atributos fisicos registrados.")
        return

    for clave, valor in datos["atributos"].items():
        print(f"  {clave:<15}: {valor}")


def mostrar_config_raw(datos):
    if not datos["lineas_config"]:
        print("Este dispositivo no tiene running-config.")
        return

    print("\n".join(datos["lineas_config"]))


def mostrar_todo(nombre, datos):
    print("\n=== IDENTIDAD Y HARDWARE ===")
    mostrar_identidad(nombre, datos)
    print("\n=== PUERTOS ===")
    mostrar_puertos(datos)
    print("\n=== ATRIBUTOS FISICOS ===")
    mostrar_atributos(datos)
    print("\n=== CONFIG COMPLETO (RAW) ===")
    mostrar_config_raw(datos)


MENU = """
1. Identidad y hardware
2. Puertos
3. Atributos fisicos
4. Config completo (raw)
5. Todo
0. Volver
"""


def menu_dispositivo(nombre, datos):
    while True:
        print(MENU)
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            return
        elif opcion == "1":
            print()
            mostrar_identidad(nombre, datos)
        elif opcion == "2":
            print()
            mostrar_puertos(datos)
        elif opcion == "3":
            print()
            mostrar_atributos(datos)
        elif opcion == "4":
            print()
            mostrar_config_raw(datos)
        elif opcion == "5":
            mostrar_todo(nombre, datos)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    dispositivos = parsear_dispositivos(ruta_xml)

    if not dispositivos:
        print(f"No se encontraron dispositivos de tipo {TIPO} en el archivo XML.")
        return

    print(f"Dispositivos disponibles: {', '.join(dispositivos.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Dispositivo: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((d for d in dispositivos if d.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro '{nombre}'. Disponibles: {', '.join(dispositivos.keys())}\n")
            continue

        menu_dispositivo(coincidencia, dispositivos[coincidencia])


if __name__ == "__main__":
    main()
