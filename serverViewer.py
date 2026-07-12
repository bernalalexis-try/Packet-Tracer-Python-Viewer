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


def parsear_servers(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    servers = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != "Server":
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else "Server"

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        port_match = re.search(r"<PORT>.*?</PORT>", bloque, re.DOTALL)
        port = port_match.group(0) if port_match else ""

        servers[nombre] = {
            "modelo": modelo,
            "serial": serial,
            "mac": _texto(port, "MACADDRESS"),
            "ip": _texto(port, "IP"),
            "mask": _texto(port, "SUBNET"),
            "gateway": _texto(port, "PORT_GATEWAY"),
            "dns": _texto(port, "PORT_DNS"),
            "bloque": bloque,
        }

    return servers


def parsear_dhcp(bloque):
    m = re.search(r"<DHCP_SERVER>.*?</DHCP_SERVER>", bloque, re.DOTALL)
    if not m:
        return {"habilitado": False, "pools": []}

    dhcp_bloque = m.group(0)
    habilitado = _texto(dhcp_bloque, "ENABLED") == "1"

    pools = []
    for pool_match in re.finditer(r"<POOL>.*?</POOL>", dhcp_bloque, re.DOTALL):
        pool = pool_match.group(0)
        cantidad_leases = len(re.findall(r"<DHCP_POOL_LEASE>", pool))
        pools.append({
            "nombre": _texto(pool, "NAME"),
            "red": _texto(pool, "NETWORK"),
            "mask": _texto(pool, "MASK"),
            "gateway": _texto(pool, "DEFAULT_ROUTER"),
            "dns": _texto(pool, "DNS_SERVER"),
            "rango": f"{_texto(pool, 'START_IP')} - {_texto(pool, 'END_IP')}",
            "max_usuarios": _texto(pool, "MAX_USERS"),
            "leases_activos": cantidad_leases,
        })

    return {"habilitado": habilitado, "pools": pools}


def parsear_dns(bloque):
    m = re.search(r"<DNS_SERVER>.*?</DNS_SERVER>", bloque, re.DOTALL)
    if not m:
        return {"habilitado": False, "registros": []}

    dns_bloque = m.group(0)
    habilitado = _texto(dns_bloque, "ENABLED") == "1"

    registros = []
    for rr_match in re.finditer(r"<RESOURCE-RECORD>.*?</RESOURCE-RECORD>", dns_bloque, re.DOTALL):
        rr = rr_match.group(0)
        registros.append({
            "tipo": _texto(rr, "TYPE"),
            "nombre": _texto(rr, "NAME"),
            "ttl": _texto(rr, "TTL"),
            "ip": _texto(rr, "IPADDRESS"),
        })

    return {"habilitado": habilitado, "registros": registros}


def parsear_http(bloque):
    m = re.search(r"<HTTP_SERVER>.*?</HTTP_SERVER>", bloque, re.DOTALL)
    if not m:
        return {"habilitado": False, "usuario": None, "password": None}

    http_bloque = m.group(0)
    return {
        "habilitado": _texto(http_bloque, "ENABLED") == "1",
        "usuario": _texto(http_bloque, "USERNAME"),
        "password": _texto(http_bloque, "PASSWORD"),
    }


def parsear_ftp(bloque):
    m = re.search(r"<FTP_SERVER>.*?</FTP_SERVER>", bloque, re.DOTALL)
    if not m:
        return {"habilitado": False, "cuentas": []}

    ftp_bloque = m.group(0)
    habilitado = _texto(ftp_bloque, "ENABLED") == "1"

    cuentas = []
    for cuenta_match in re.finditer(r"<ACCOUNT>.*?</ACCOUNT>", ftp_bloque, re.DOTALL):
        cuenta = cuenta_match.group(0)
        cuentas.append({
            "usuario": _texto(cuenta, "USERNAME"),
            "password": _texto(cuenta, "PASSWORD"),
            "permisos": _texto(cuenta, "PERMISSIONS"),
        })

    return {"habilitado": habilitado, "cuentas": cuentas}


def parsear_email(bloque):
    m = re.search(r"<EMAIL_SERVER>.*?</EMAIL_SERVER>", bloque, re.DOTALL)
    if not m:
        return {"smtp": False, "pop3": False, "dominio": None, "usuarios": None}

    email_bloque = m.group(0)
    return {
        "smtp": _texto(email_bloque, "SMTP_ENABLED") == "1",
        "pop3": _texto(email_bloque, "POP3_ENABLED") == "1",
        "dominio": _texto(email_bloque, "SMTP_DOMAIN"),
        "usuarios": _texto(email_bloque, "NO_OF_USERS"),
    }


def mostrar_identidad(nombre, datos):
    print(f"Hostname     : {nombre}")
    print(f"Modelo       : {datos['modelo']}")
    print(f"Numero serie : {datos['serial']}")


def mostrar_red(datos):
    print(f"IP      : {datos['ip'] or 'sin configurar'}")
    print(f"Mascara : {datos['mask'] or 'sin configurar'}")
    print(f"Gateway : {datos['gateway'] or 'sin configurar'}")
    print(f"DNS     : {datos['dns'] or 'sin configurar'}")
    print(f"MAC     : {datos['mac'] or 'desconocida'}")


def mostrar_servicios(bloque):
    dhcp = parsear_dhcp(bloque)
    dns = parsear_dns(bloque)
    http = parsear_http(bloque)
    ftp = parsear_ftp(bloque)
    email = parsear_email(bloque)

    def estado(valor):
        return "habilitado" if valor else "deshabilitado"

    print(f"DHCP : {estado(dhcp['habilitado'])}")
    print(f"DNS  : {estado(dns['habilitado'])}")
    print(f"HTTP : {estado(http['habilitado'])}")
    print(f"FTP  : {estado(ftp['habilitado'])}")
    print(f"SMTP : {estado(email['smtp'])}")
    print(f"POP3 : {estado(email['pop3'])}")


def mostrar_dhcp(bloque):
    dhcp = parsear_dhcp(bloque)
    if not dhcp["habilitado"]:
        print("Servicio DHCP deshabilitado.")
        return

    if not dhcp["pools"]:
        print("DHCP habilitado, sin pools configurados.")
        return

    for pool in dhcp["pools"]:
        print(f"\nPool: {pool['nombre']}")
        print(f"  Red          : {pool['red']} {pool['mask']}")
        print(f"  Gateway      : {pool['gateway']}")
        print(f"  DNS          : {pool['dns']}")
        print(f"  Rango        : {pool['rango']}")
        print(f"  Max usuarios : {pool['max_usuarios']}")
        print(f"  Leases activos: {pool['leases_activos']}")


def mostrar_dns(bloque):
    dns = parsear_dns(bloque)
    if not dns["habilitado"]:
        print("Servicio DNS deshabilitado.")
        return

    if not dns["registros"]:
        print("DNS habilitado, sin registros configurados.")
        return

    for r in dns["registros"]:
        print(f"  {r['tipo']:<8} {r['nombre']:<35} -> {r['ip']}  (TTL {r['ttl']})")


def mostrar_http(bloque):
    http = parsear_http(bloque)
    if not http["habilitado"]:
        print("Servicio HTTP deshabilitado.")
        return

    print("Servicio HTTP habilitado.")
    print(f"Usuario  : {http['usuario'] or 'sin autenticacion'}")
    print(f"Password : {http['password'] or 'sin autenticacion'}")


def mostrar_ftp(bloque):
    ftp = parsear_ftp(bloque)
    if not ftp["habilitado"]:
        print("Servicio FTP deshabilitado.")
        return

    if not ftp["cuentas"]:
        print("FTP habilitado, sin cuentas configuradas.")
        return

    for c in ftp["cuentas"]:
        print(f"  Usuario: {c['usuario']:<15} Password: {c['password']:<15} Permisos: {c['permisos']}")


def mostrar_email(bloque):
    email = parsear_email(bloque)
    print(f"SMTP    : {'habilitado' if email['smtp'] else 'deshabilitado'}")
    print(f"POP3    : {'habilitado' if email['pop3'] else 'deshabilitado'}")
    print(f"Dominio : {email['dominio'] or 'sin configurar'}")
    print(f"Usuarios: {email['usuarios'] or '0'}")


def mostrar_todo(nombre, datos):
    print("\n=== IDENTIDAD Y HARDWARE ===")
    mostrar_identidad(nombre, datos)
    print("\n=== CONFIGURACION DE RED ===")
    mostrar_red(datos)
    print("\n=== SERVICIOS HABILITADOS ===")
    mostrar_servicios(datos["bloque"])
    print("\n=== DHCP ===")
    mostrar_dhcp(datos["bloque"])
    print("\n=== DNS ===")
    mostrar_dns(datos["bloque"])
    print("\n=== HTTP ===")
    mostrar_http(datos["bloque"])
    print("\n=== FTP ===")
    mostrar_ftp(datos["bloque"])
    print("\n=== EMAIL ===")
    mostrar_email(datos["bloque"])


MENU = """
1. Identidad y hardware
2. Configuracion de red
3. Servicios habilitados
4. DHCP
5. DNS
6. HTTP
7. FTP
8. Email
9. Todo
0. Volver
"""


def menu_server(nombre, datos):
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
            mostrar_servicios(datos["bloque"])
        elif opcion == "4":
            print()
            mostrar_dhcp(datos["bloque"])
        elif opcion == "5":
            print()
            mostrar_dns(datos["bloque"])
        elif opcion == "6":
            print()
            mostrar_http(datos["bloque"])
        elif opcion == "7":
            print()
            mostrar_ftp(datos["bloque"])
        elif opcion == "8":
            print()
            mostrar_email(datos["bloque"])
        elif opcion == "9":
            mostrar_todo(nombre, datos)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    servers = parsear_servers(ruta_xml)

    if not servers:
        print("No se encontraron servers en el archivo XML.")
        return

    print(f"Servers disponibles: {', '.join(servers.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Server: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((s for s in servers if s.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro '{nombre}'. Disponibles: {', '.join(servers.keys())}\n")
            continue

        menu_server(coincidencia, servers[coincidencia])


if __name__ == "__main__":
    main()
