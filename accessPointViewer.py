import glob
import os
import re
import sys


def encontrar_xml():
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = glob.glob(os.path.join(base, "*.xml"))
    if not candidatos:
        print("No se encontró ningún archivo .xml en esta carpeta.")
        sys.exit(1)
    return candidatos[0]


def _texto(bloque, tag):
    m = re.search(rf"<{tag}>([^<]*)</{tag}>", bloque)
    return m.group(1) if m and m.group(1) else None


def parsear_access_points(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    aps = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != "AccessPoint":
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else "AccessPoint"

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        macs = re.findall(r"<MACADDRESS>([^<]*)</MACADDRESS>", bloque)
        mac_ethernet = macs[0] if len(macs) > 0 else None
        mac_wireless = macs[1] if len(macs) > 1 else None

        wireless_match = re.search(r"<WIRELESS_SERVER>.*?</WIRELESS_SERVER>", bloque, re.DOTALL)
        wireless = wireless_match.group(0) if wireless_match else ""

        aps[nombre] = {
            "modelo": modelo,
            "serial": serial,
            "mac_ethernet": mac_ethernet,
            "mac_wireless": mac_wireless,
            "ssid": _texto(wireless, "SSID"),
            "network_mode": _texto(wireless, "NETWORK_MODE"),
            "canal": _texto(wireless, "STANDARD_CHANNEL"),
            "banda": _texto(wireless, "RADIO_BAND"),
            "ssid_broadcast": _texto(wireless, "SSID_BROADCAST_ENABLED") == "1",
            "mac_filter": _texto(wireless, "MAC_FILTER_ENABLED") == "1",
            "encrypt_type": _texto(wireless, "ENCRYPT_TYPE"),
            "authen_type": _texto(wireless, "AUTHEN_TYPE"),
            "clave": _texto(wireless, "KEY"),
        }

    return aps


def mostrar_identidad(nombre, datos):
    print(f"Hostname     : {nombre}")
    print(f"Modelo       : {datos['modelo']}")
    print(f"Numero serie : {datos['serial']}")


def mostrar_red(datos):
    print(f"MAC puerto Ethernet : {datos['mac_ethernet'] or 'desconocida'}")
    print(f"MAC puerto Wireless : {datos['mac_wireless'] or 'desconocida'}")


def mostrar_wifi(datos):
    print(f"SSID              : {datos['ssid'] or 'sin configurar'}")
    print(f"Modo de red (codigo): {datos['network_mode'] or 'sin configurar'}")
    print(f"Canal             : {datos['canal'] or 'automático'}")
    print(f"Difusion de SSID  : {'si' if datos['ssid_broadcast'] else 'no (oculto)'}")
    print(f"Filtro de MAC     : {'habilitado' if datos['mac_filter'] else 'deshabilitado'}")
    print("Nota: el codigo de 'Modo de red' corresponde al combo 'Network Mode' del AP en Packet Tracer.")


def mostrar_seguridad(datos):
    print(f"Tipo de cifrado (codigo)       : {datos['encrypt_type'] or 'sin configurar'}")
    print(f"Tipo de autenticacion (codigo) : {datos['authen_type'] or 'sin configurar'}")
    print(f"Clave configurada              : {datos['clave'] or 'sin clave (red abierta)'}")
    print("Nota: los codigos corresponden al combo 'Security' del AP en Packet Tracer.")


def mostrar_todo(nombre, datos):
    print("\n=== IDENTIDAD Y HARDWARE ===")
    mostrar_identidad(nombre, datos)
    print("\n=== CONFIGURACION DE RED ===")
    mostrar_red(datos)
    print("\n=== RED INALAMBRICA ===")
    mostrar_wifi(datos)
    print("\n=== SEGURIDAD ===")
    mostrar_seguridad(datos)


MENU = """
1. Identidad y hardware
2. Configuracion de red
3. Red inalambrica
4. Seguridad
5. Todo
0. Volver
"""


def menu_ap(nombre, datos):
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
            mostrar_red(datos)
        elif opcion == "3":
            print()
            mostrar_wifi(datos)
        elif opcion == "4":
            print()
            mostrar_seguridad(datos)
        elif opcion == "5":
            mostrar_todo(nombre, datos)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    aps = parsear_access_points(ruta_xml)

    if not aps:
        print("No se encontraron Access Points en el archivo XML.")
        return

    print(f"Access Points disponibles: {', '.join(aps.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Access Point: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((a for a in aps if a.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro '{nombre}'. Disponibles: {', '.join(aps.keys())}\n")
            continue

        menu_ap(coincidencia, aps[coincidencia])


if __name__ == "__main__":
    main()
