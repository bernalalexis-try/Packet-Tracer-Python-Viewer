import re

try:
    from viewers.comun import (
        agregar_dispositivo,
        atributos_extendidos,
        bloques_device,
        decodificar,
        encontrar_xml,
        leer_xml,
        texto,
    )
except ImportError:  # al correrlo directo desde la carpeta viewers
    from comun import (
        agregar_dispositivo,
        atributos_extendidos,
        bloques_device,
        decodificar,
        encontrar_xml,
        leer_xml,
        texto,
    )


def parsear_dispositivos(ruta_xml, tipos, nombre_por_defecto):
    dispositivos = {}
    for bloque in bloques_device(leer_xml(ruta_xml)):
        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() not in tipos:
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else nombre_por_defecto

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        rc_match = re.search(r"<RUNNINGCONFIG>(.*?)</RUNNINGCONFIG>", bloque, re.DOTALL)
        lineas_config = re.findall(r"<LINE>(.*?)</LINE>", rc_match.group(1)) if rc_match else []

        datos = {
            "tipo": tipo_match.group(1).strip(),
            "modelo": modelo,
            "serial": serial,
            "encendido": texto(bloque, "POWER") == "true",
            "macs": re.findall(r"<MACADDRESS>([^<]*)</MACADDRESS>", bloque),
            "atributos": atributos_extendidos(bloque),
            "lineas_config": lineas_config,
        }
        agregar_dispositivo(dispositivos, decodificar(nombre), decodificar(datos))

    return dispositivos


def mostrar_identidad(nombre, datos):
    print(f"Nombre       : {nombre}")
    print(f"Tipo         : {datos['tipo']}")
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


def main(parsear, mensaje_sin_dispositivos):
    """Menú para usar un viewer por separado, sin pasar por main.py."""
    dispositivos = parsear(encontrar_xml())

    if not dispositivos:
        print(mensaje_sin_dispositivos)
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
