import glob
import os
import re
import sys


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


def parsear_hosts(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    hosts = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() not in ("Smart Phone", "Tablet PC"):
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else "Dispositivo"

        port_match = re.search(r"<PORT>.*?</PORT>", bloque, re.DOTALL)
        port = port_match.group(0) if port_match else ""

        hosts[nombre] = {
            "tipo": tipo_match.group(1).strip(),
            "mac": _texto(port, "MACADDRESS"),
            "dhcp": _texto(port, "PORT_DHCP_ENABLE") == "true",
            "ip": _texto(port, "IP"),
            "mask": _texto(port, "SUBNET"),
            "gateway": _texto(port, "PORT_GATEWAY"),
            "dns": _texto(port, "PORT_DNS"),
        }

    return hosts


def parsear_leases_dhcp(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    leases = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != "Server":
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre_servidor = nombre_match.group(1).strip() if nombre_match else "Server"

        dhcp_match = re.search(r"<DHCP_SERVER>.*?</DHCP_SERVER>", bloque, re.DOTALL)
        if not dhcp_match:
            continue
        dhcp_bloque = dhcp_match.group(0)

        if _texto(dhcp_bloque, "ENABLED") != "1":
            continue

        for pool_match in re.finditer(r"<POOL>.*?</POOL>", dhcp_bloque, re.DOTALL):
            pool = pool_match.group(0)
            nombre_pool = _texto(pool, "NAME")

            for lease_match in re.finditer(r"<DHCP_POOL_LEASE>.*?</DHCP_POOL_LEASE>", pool, re.DOTALL):
                lease = lease_match.group(0)
                mac = _texto(lease, "MAC_ADDRESS")
                ip = _texto(lease, "IP_ADDRESS")
                if mac and ip:
                    leases[mac] = {"ip": ip, "pool": nombre_pool, "servidor": nombre_servidor}

    return leases


def mostrar_identidad(nombre, datos):
    print(f"Nombre       : {nombre}")
    print(f"Tipo         : {datos['tipo']}")
    print(f"MAC          : {datos['mac'] or 'desconocida'}")


def mostrar_red(datos, leases):
    if datos["dhcp"]:
        print("Configuracion: DHCP (automatica)")
        lease = leases.get(datos["mac"])
        if lease:
            print(f"IP asignada  : {lease['ip']}")
            print(f"Pool DHCP    : {lease['pool']}")
            print(f"Servidor DHCP: {lease['servidor']}")
        else:
            print("IP asignada  : sin lease registrado (no obtuvo IP aun)")
    else:
        print("Configuracion: Estatica")
        print(f"IP           : {datos['ip'] or 'sin configurar'}")
        print(f"Mascara      : {datos['mask'] or 'sin configurar'}")
        print(f"Gateway      : {datos['gateway'] or 'sin configurar'}")
        print(f"DNS          : {datos['dns'] or 'sin configurar'}")


def mostrar_todo(nombre, datos, leases):
    print("\n=== IDENTIDAD ===")
    mostrar_identidad(nombre, datos)
    print("\n=== CONFIGURACION DE RED ===")
    mostrar_red(datos, leases)


MENU = """
1. Identidad
2. Configuracion de red
3. Todo
0. Volver
"""


def menu_host(nombre, datos, leases):
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
            mostrar_red(datos, leases)
        elif opcion == "3":
            mostrar_todo(nombre, datos, leases)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    hosts = parsear_hosts(ruta_xml)
    leases = parsear_leases_dhcp(ruta_xml)

    if not hosts:
        print("No se encontraron Smartphones ni Tablets en el archivo XML.")
        return

    print(f"Dispositivos disponibles: {', '.join(hosts.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Smartphone/Tablet: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((h for h in hosts if h.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro '{nombre}'. Disponibles: {', '.join(hosts.keys())}\n")
            continue

        menu_host(coincidencia, hosts[coincidencia], leases)


if __name__ == "__main__":
    main()
