import re

try:
    from viewers.comun import agregar_dispositivo, decodificar, encontrar_xml
except ImportError:  # al correrlo directo: py viewers/pcViewer.py
    from comun import agregar_dispositivo, decodificar, encontrar_xml


def _texto(bloque, tag):
    m = re.search(rf"<{tag}>([^<]*)</{tag}>", bloque)
    return m.group(1) if m and m.group(1) else None


TIPOS = ("Pc", "Laptop")


def parsear_hosts(ruta_xml, tipos=TIPOS, nombre_por_defecto="PC"):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    hosts = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() not in tipos:
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else nombre_por_defecto

        port_match = re.search(r"<PORT>.*?</PORT>", bloque, re.DOTALL)
        port = port_match.group(0) if port_match else ""

        datos = {
            "tipo": tipo_match.group(1).strip(),
            "mac": _texto(port, "MACADDRESS"),
            "dhcp": _texto(port, "PORT_DHCP_ENABLE") == "true",
            "ip": _texto(port, "IP"),
            "mask": _texto(port, "SUBNET"),
            "gateway": _texto(port, "PORT_GATEWAY"),
            "dns": _texto(port, "PORT_DNS"),
        }
        agregar_dispositivo(hosts, decodificar(nombre), decodificar(datos))

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

    return decodificar(leases)


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
            if datos["ip"]:
                aclaracion = " (APIPA: no le respondio ningun DHCP)" if datos["ip"].startswith("169.254.") else ""
                print(f"IP del puerto: {datos['ip']} {datos['mask'] or ''}".rstrip() + aclaracion)
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


def main(
    parsear=parsear_hosts,
    mensaje_sin_dispositivos="No se encontraron PCs ni Laptops en el archivo XML.",
    titulo="Hosts",
    prompt="PC/Laptop: ",
):
    ruta_xml = encontrar_xml()
    hosts = parsear(ruta_xml)
    leases = parsear_leases_dhcp(ruta_xml)

    if not hosts:
        print(mensaje_sin_dispositivos)
        return

    print(f"{titulo} disponibles: {', '.join(hosts.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input(prompt).strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((h for h in hosts if h.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro '{nombre}'. Disponibles: {', '.join(hosts.keys())}\n")
            continue

        menu_host(coincidencia, hosts[coincidencia], leases)


if __name__ == "__main__":
    main()
