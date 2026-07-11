import glob
import os
import re
import sys


def ip_to_int(ip):
    a, b, c, d = (int(o) for o in ip.split("."))
    return (a << 24) | (b << 16) | (c << 8) | d


def int_to_ip(value):
    return f"{(value >> 24) & 0xFF}.{(value >> 16) & 0xFF}.{(value >> 8) & 0xFF}.{value & 0xFF}"


def mask_to_prefixlen(mask):
    return bin(ip_to_int(mask)).count("1")


def network_address(ip, prefixlen):
    if prefixlen == 0:
        return 0
    full_mask = (0xFFFFFFFF << (32 - prefixlen)) & 0xFFFFFFFF
    return ip_to_int(ip) & full_mask


def classful_info(network_int):
    primer_octeto = (network_int >> 24) & 0xFF
    if 1 <= primer_octeto <= 126:
        classful_len = 8
    elif 128 <= primer_octeto <= 191:
        classful_len = 16
    elif 192 <= primer_octeto <= 223:
        classful_len = 24
    else:
        classful_len = 8
    major = network_address(int_to_ip(network_int), classful_len)
    return classful_len, major


def encontrar_xml():
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = glob.glob(os.path.join(base, "*.xml"))
    if not candidatos:
        print("No se encontró ningún archivo .xml en esta carpeta.")
        sys.exit(1)
    return candidatos[0]


def parsear_routers(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    routers = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != "Router":
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else "Router"

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        rc_match = re.search(r"<RUNNINGCONFIG>(.*?)</RUNNINGCONFIG>", bloque, re.DOTALL)
        if not rc_match:
            continue

        lineas = re.findall(r"<LINE>(.*?)</LINE>", rc_match.group(1))

        routers[nombre] = {
            "modelo": modelo,
            "serial": serial,
            "lineas": lineas,
        }

    return routers


def parsear_interfaces(lineas):
    interfaces = []
    actual = None

    for linea in lineas:
        if not linea.startswith(" ") and linea.lower().startswith("interface "):
            if actual:
                interfaces.append(actual)
            actual = {
                "nombre": linea.split(" ", 1)[1].strip(),
                "ip": None,
                "mask": None,
                "up": True,
                "descripcion": None,
                "duplex": None,
                "velocidad": None,
                "mtu": None,
                "vlan": None,
            }
            continue

        if actual is None:
            continue

        contenido = linea.strip()
        if contenido == "!" or (not linea.startswith(" ") and contenido != ""):
            interfaces.append(actual)
            actual = None
            continue

        m_ip = re.match(r"ip address (\d{1,3}(?:\.\d{1,3}){3}) (\d{1,3}(?:\.\d{1,3}){3})", contenido)
        m_desc = re.match(r"description (.+)", contenido)
        m_duplex = re.match(r"duplex (\S+)", contenido)
        m_speed = re.match(r"speed (\S+)", contenido)
        m_mtu = re.match(r"mtu (\d+)", contenido)
        m_vlan = re.match(r"encapsulation dot1Q (\d+)", contenido)

        if m_ip:
            actual["ip"], actual["mask"] = m_ip.group(1), m_ip.group(2)
        elif contenido == "shutdown":
            actual["up"] = False
        elif m_desc:
            actual["descripcion"] = m_desc.group(1)
        elif m_duplex:
            actual["duplex"] = m_duplex.group(1)
        elif m_speed:
            actual["velocidad"] = m_speed.group(1)
        elif m_mtu:
            actual["mtu"] = m_mtu.group(1)
        elif m_vlan:
            actual["vlan"] = m_vlan.group(1)

    if actual:
        interfaces.append(actual)

    return interfaces


def parsear_rutas_estaticas(lineas):
    rutas = []
    for linea in lineas:
        contenido = linea.strip()
        m = re.match(
            r"ip route (\d{1,3}(?:\.\d{1,3}){3}) (\d{1,3}(?:\.\d{1,3}){3}) (\S+)",
            contenido,
        )
        if m:
            rutas.append({
                "red": m.group(1),
                "mask": m.group(2),
                "next_hop": m.group(3),
            })
    return rutas


def parsear_version_ios(lineas):
    for linea in lineas:
        m = re.match(r"version (\S+)", linea.strip())
        if m:
            return m.group(1)
    return "Desconocida"


def parsear_seguridad(lineas):
    enable_secret = None
    enable_password = None
    con_password = None
    vty_password = None
    vty_login = False

    seccion = None
    for linea in lineas:
        contenido = linea.strip()

        m_secret = re.match(r"enable secret (?:5 )?(\S+)", contenido)
        m_enable_pw = re.match(r"enable password (\S+)", contenido)
        if m_secret:
            enable_secret = m_secret.group(1)
        elif m_enable_pw:
            enable_password = m_enable_pw.group(1)

        if not linea.startswith(" ") and contenido.startswith("line con"):
            seccion = "con"
            continue
        if not linea.startswith(" ") and contenido.startswith("line vty"):
            seccion = "vty"
            continue
        if not linea.startswith(" ") and contenido != "":
            seccion = None

        if seccion == "con":
            m_pw = re.match(r"password (\S+)", contenido)
            if m_pw:
                con_password = m_pw.group(1)
        if seccion == "vty":
            m_pw = re.match(r"password (\S+)", contenido)
            if m_pw:
                vty_password = m_pw.group(1)
            if contenido == "login":
                vty_login = True

    acls = [l.strip() for l in lineas if l.strip().startswith("access-list")]

    return {
        "enable_secret": enable_secret,
        "enable_password": enable_password,
        "con_password": con_password,
        "vty_password": vty_password,
        "vty_login": vty_login,
        "acls": acls,
    }


def parsear_nat(lineas):
    interfaces_nat = []
    reglas = []
    interfaz_actual = None

    for linea in lineas:
        if not linea.startswith(" ") and linea.lower().startswith("interface "):
            interfaz_actual = linea.split(" ", 1)[1].strip()
            continue

        contenido = linea.strip()
        if contenido == "ip nat inside":
            interfaces_nat.append((interfaz_actual, "inside"))
        elif contenido == "ip nat outside":
            interfaces_nat.append((interfaz_actual, "outside"))
        elif contenido.startswith("ip nat "):
            reglas.append(contenido)

    return {"interfaces": interfaces_nat, "reglas": reglas}


def parsear_dhcp(lineas):
    pools = []
    pool_actual = None

    for linea in lineas:
        contenido = linea.strip()
        m_pool = re.match(r"ip dhcp pool (\S+)", contenido)
        if m_pool and not linea.startswith(" "):
            pool_actual = {"nombre": m_pool.group(1), "red": None, "gateway": None, "dns": None}
            pools.append(pool_actual)
            continue

        if pool_actual is None:
            continue

        if not linea.startswith(" ") and contenido != "":
            pool_actual = None
            continue

        m_red = re.match(r"network (\S+) (\S+)", contenido)
        m_gw = re.match(r"default-router (\S+)", contenido)
        m_dns = re.match(r"dns-server (\S+)", contenido)
        if m_red:
            pool_actual["red"] = f"{m_red.group(1)} {m_red.group(2)}"
        elif m_gw:
            pool_actual["gateway"] = m_gw.group(1)
        elif m_dns:
            pool_actual["dns"] = m_dns.group(1)

    return pools


def construir_entradas(interfaces, rutas_estaticas):
    entradas = {}

    for intf in interfaces:
        if not intf["ip"] or not intf["up"]:
            continue
        prefixlen = mask_to_prefixlen(intf["mask"])
        red = network_address(intf["ip"], prefixlen)

        entradas[(red, prefixlen)] = {"codigo": "C", "via": [], "interfaz": intf["nombre"]}
        entradas[(ip_to_int(intf["ip"]), 32)] = {"codigo": "L", "via": [], "interfaz": intf["nombre"]}

    for ruta in rutas_estaticas:
        prefixlen = mask_to_prefixlen(ruta["mask"])
        red = network_address(ruta["red"], prefixlen)
        clave = (red, prefixlen)

        if clave in entradas and entradas[clave]["codigo"] in ("C", "L"):
            continue

        if clave not in entradas:
            entradas[clave] = {"codigo": "S", "via": [], "interfaz": None}
        entradas[clave]["via"].append(ruta["next_hop"])

    return entradas


def agrupar_por_mayor(entradas):
    grupos = {}
    for (red, prefixlen), datos in entradas.items():
        classful_len, major = classful_info(red)
        clave_grupo = (major, classful_len)
        grupos.setdefault(clave_grupo, []).append((red, prefixlen, datos))
    return grupos


def formatear_tabla_rutas(interfaces, rutas_estaticas):
    entradas = construir_entradas(interfaces, rutas_estaticas)
    grupos = agrupar_por_mayor(entradas)

    salida = []

    clave_default = (0, 0)
    if clave_default in entradas:
        datos = entradas[clave_default]
        prefijo = "S*    0.0.0.0/0 "
        for i, via in enumerate(sorted(datos["via"])):
            if i == 0:
                salida.append(f"{prefijo}[1/0] via {via}")
            else:
                salida.append(f"{' ' * len(prefijo)}[1/0] via {via}")

    for (major, classful_len) in sorted(grupos.keys()):
        rutas_grupo = sorted(grupos[(major, classful_len)], key=lambda r: r[0])
        rutas_grupo = [r for r in rutas_grupo if not (r[0] == 0 and r[1] == 0)]
        if not rutas_grupo:
            continue

        masks = {r[1] for r in rutas_grupo}
        es_standalone = len(rutas_grupo) == 1 and rutas_grupo[0][1] == classful_len

        if es_standalone:
            red, prefixlen, datos = rutas_grupo[0]
            salida.append(_formatear_entrada_ruta(red, prefixlen, datos, indentado=False))
        else:
            texto_masks = (
                f"is variably subnetted, {len(rutas_grupo)} subnets, {len(masks)} masks"
                if len(masks) > 1
                else f"is subnetted, {len(rutas_grupo)} subnets"
            )
            salida.append(f"     {int_to_ip(major)}/{classful_len} {texto_masks}")
            for red, prefixlen, datos in rutas_grupo:
                salida.append(_formatear_entrada_ruta(red, prefixlen, datos, indentado=True))

    return "\n".join(salida) if salida else "Sin rutas."


def _formatear_entrada_ruta(red, prefixlen, datos, indentado):
    espacios = 7 if indentado else 4
    prefijo = f"{datos['codigo']}{' ' * espacios}{int_to_ip(red)}/{prefixlen} "

    if datos["codigo"] in ("C", "L"):
        return f"{prefijo}is directly connected, {datos['interfaz']}"

    lineas = []
    for i, via in enumerate(datos["via"]):
        if i == 0:
            lineas.append(f"{prefijo}[1/0] via {via}")
        else:
            lineas.append(f"{' ' * len(prefijo)}[1/0] via {via}")
    return "\n".join(lineas)


def mostrar_identidad(nombre, datos_router):
    lineas = datos_router["lineas"]
    version = parsear_version_ios(lineas)
    print(f"Hostname     : {nombre}")
    print(f"Modelo       : {datos_router['modelo']}")
    print(f"Numero serie : {datos_router['serial']}")
    print(f"Version IOS  : {version}")


def mostrar_interfaces(lineas):
    interfaces = parsear_interfaces(lineas)
    if not interfaces:
        print("Sin interfaces configuradas.")
        return

    for intf in interfaces:
        estado = "up" if intf["up"] else "administratively down"
        print(f"\n{intf['nombre']}  [{estado}]")
        print(f"  IP           : {intf['ip'] or 'sin IP'} {intf['mask'] or ''}".rstrip())
        if intf["descripcion"]:
            print(f"  Descripcion  : {intf['descripcion']}")
        if intf["vlan"]:
            print(f"  VLAN (dot1Q) : {intf['vlan']}")
        if intf["duplex"]:
            print(f"  Duplex       : {intf['duplex']}")
        if intf["velocidad"]:
            print(f"  Velocidad    : {intf['velocidad']}")
        if intf["mtu"]:
            print(f"  MTU          : {intf['mtu']}")


def mostrar_ruteo(lineas):
    interfaces = parsear_interfaces(lineas)
    rutas_estaticas = parsear_rutas_estaticas(lineas)
    print(formatear_tabla_rutas(interfaces, rutas_estaticas))

    if rutas_estaticas:
        print("\nRutas estaticas configuradas:")
        for r in rutas_estaticas:
            print(f"  ip route {r['red']} {r['mask']} {r['next_hop']}")


def mostrar_seguridad(lineas):
    seguridad = parsear_seguridad(lineas)

    print(f"Enable secret   : {seguridad['enable_secret'] or 'no configurado'}")
    print(f"Enable password : {seguridad['enable_password'] or 'no configurado'}")
    print(f"Password consola: {seguridad['con_password'] or 'no configurada'}")
    print(f"Password VTY    : {seguridad['vty_password'] or 'no configurada'}")
    print(f"Login en VTY    : {'si' if seguridad['vty_login'] else 'no'}")

    if seguridad["acls"]:
        print("\nACLs configuradas:")
        for acl in seguridad["acls"]:
            print(f"  {acl}")
    else:
        print("\nSin ACLs configuradas.")


def mostrar_red(lineas):
    interfaces = parsear_interfaces(lineas)
    subinterfaces = [i for i in interfaces if i["vlan"]]

    print("Subinterfaces / VLANs:")
    if subinterfaces:
        for intf in subinterfaces:
            print(f"  {intf['nombre']}  VLAN {intf['vlan']}  IP {intf['ip']}/{intf['mask']}")
    else:
        print("  Sin subinterfaces configuradas.")

    nat = parsear_nat(lineas)
    print("\nNAT:")
    if nat["interfaces"] or nat["reglas"]:
        for iface, tipo in nat["interfaces"]:
            print(f"  {iface}: {tipo}")
        for regla in nat["reglas"]:
            print(f"  {regla}")
    else:
        print("  Sin NAT configurado.")

    dhcp = parsear_dhcp(lineas)
    print("\nDHCP:")
    if dhcp:
        for pool in dhcp:
            print(f"  Pool {pool['nombre']}: red {pool['red']}, gateway {pool['gateway']}, dns {pool['dns']}")
    else:
        print("  Sin pools DHCP configurados.")


def mostrar_todo(nombre, datos_router):
    print("\n=== IDENTIDAD Y HARDWARE ===")
    mostrar_identidad(nombre, datos_router)
    print("\n=== INTERFACES ===")
    mostrar_interfaces(datos_router["lineas"])
    print("\n=== RUTEO ===")
    mostrar_ruteo(datos_router["lineas"])
    print("\n=== SEGURIDAD ===")
    mostrar_seguridad(datos_router["lineas"])
    print("\n=== RED (VLANs / NAT / DHCP) ===")
    mostrar_red(datos_router["lineas"])


MENU = """
1. Identidad y hardware
2. Interfaces
3. Ruteo
4. Seguridad
5. Red (VLANs / NAT / DHCP)
6. Todo
0. Volver
"""


def menu_router(nombre, datos_router):
    while True:
        print(MENU)
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            return
        elif opcion == "1":
            print()
            mostrar_identidad(nombre, datos_router)
        elif opcion == "2":
            print()
            mostrar_interfaces(datos_router["lineas"])
        elif opcion == "3":
            print()
            mostrar_ruteo(datos_router["lineas"])
        elif opcion == "4":
            print()
            mostrar_seguridad(datos_router["lineas"])
        elif opcion == "5":
            print()
            mostrar_red(datos_router["lineas"])
        elif opcion == "6":
            mostrar_todo(nombre, datos_router)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    routers = parsear_routers(ruta_xml)

    if not routers:
        print("No se encontraron routers en el archivo XML.")
        return

    print(f"Routers disponibles: {', '.join(routers.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Router: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((r for r in routers if r.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro el router '{nombre}'. Disponibles: {', '.join(routers.keys())}\n")
            continue

        menu_router(coincidencia, routers[coincidencia])


if __name__ == "__main__":
    main()
