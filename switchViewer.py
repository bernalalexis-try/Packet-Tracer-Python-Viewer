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


def parsear_switches(ruta_xml):
    with open(ruta_xml, "r", encoding="utf-8") as f:
        contenido = f.read()

    switches = {}
    for match in re.finditer(r"<DEVICE>.*?</DEVICE>", contenido, re.DOTALL):
        bloque = match.group(0)

        tipo_match = re.search(r"<TYPE[^>]*>([^<]*)</TYPE>", bloque)
        if not tipo_match or tipo_match.group(1).strip() != "Switch":
            continue

        nombre_match = re.search(r'<NAME translate="true">([^<]*)</NAME>', bloque)
        nombre = nombre_match.group(1).strip() if nombre_match else "Switch"

        modelo_match = re.search(r'<TYPE[^>]*model="([^"]*)"', bloque)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serial_match = re.search(r"<SERIALNUMBER>([^<]*)</SERIALNUMBER>", bloque)
        serial = serial_match.group(1) if serial_match else "Desconocido"

        rc_match = re.search(r"<RUNNINGCONFIG>(.*?)</RUNNINGCONFIG>", bloque, re.DOTALL)
        lineas = re.findall(r"<LINE>(.*?)</LINE>", rc_match.group(1)) if rc_match else []

        vlans_crudas = re.findall(r'<VLAN name="([^"]*)" number="(\d+)"', bloque)
        vlans = {}
        for nombre_vlan, numero in vlans_crudas:
            vlans[int(numero)] = nombre_vlan
        vlans_ordenadas = [(n, vlans[n]) for n in sorted(vlans)]

        switches[nombre] = {
            "modelo": modelo,
            "serial": serial,
            "lineas": lineas,
            "vlans": vlans_ordenadas,
        }

    return switches


def parsear_version_ios(lineas):
    for linea in lineas:
        m = re.match(r"version (\S+)", linea.strip())
        if m:
            return m.group(1)
    return "Desconocida"


def parsear_puertos(lineas):
    puertos = []
    actual = None

    for linea in lineas:
        if not linea.startswith(" ") and linea.lower().startswith("interface "):
            if actual:
                puertos.append(actual)
            actual = {
                "nombre": linea.split(" ", 1)[1].strip(),
                "modo": None,
                "vlan_access": None,
                "vlan_trunk": None,
                "descripcion": None,
                "duplex": None,
                "velocidad": None,
                "up": True,
            }
            continue

        if actual is None:
            continue

        contenido = linea.strip()
        if contenido == "!" or (not linea.startswith(" ") and contenido != ""):
            puertos.append(actual)
            actual = None
            continue

        m_modo = re.match(r"switchport mode (\S+)", contenido)
        m_access = re.match(r"switchport access vlan (\d+)", contenido)
        m_trunk = re.match(r"switchport trunk allowed vlan (\S+)", contenido)
        m_desc = re.match(r"description (.+)", contenido)
        m_duplex = re.match(r"duplex (\S+)", contenido)
        m_speed = re.match(r"speed (\S+)", contenido)

        if m_modo:
            actual["modo"] = m_modo.group(1)
        elif m_access:
            actual["vlan_access"] = m_access.group(1)
        elif m_trunk:
            actual["vlan_trunk"] = m_trunk.group(1)
        elif m_desc:
            actual["descripcion"] = m_desc.group(1)
        elif m_duplex:
            actual["duplex"] = m_duplex.group(1)
        elif m_speed:
            actual["velocidad"] = m_speed.group(1)
        elif contenido == "shutdown":
            actual["up"] = False

    if actual:
        puertos.append(actual)

    return puertos


def parsear_seguridad(lineas):
    enable_secret = None
    enable_password = None
    con_password = None
    vty_password = None
    vty_login = False
    port_security = []

    seccion = None
    interfaz_actual = None

    for linea in lineas:
        contenido = linea.strip()

        if not linea.startswith(" ") and linea.lower().startswith("interface "):
            interfaz_actual = linea.split(" ", 1)[1].strip()

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

        if contenido.startswith("switchport port-security"):
            port_security.append((interfaz_actual, contenido))

    return {
        "enable_secret": enable_secret,
        "enable_password": enable_password,
        "con_password": con_password,
        "vty_password": vty_password,
        "vty_login": vty_login,
        "port_security": port_security,
    }


def parsear_spanning_tree(lineas):
    modo = None
    prioridades = []

    for linea in lineas:
        contenido = linea.strip()
        m_modo = re.match(r"spanning-tree mode (\S+)", contenido)
        m_prio = re.match(r"spanning-tree vlan (\S+) priority (\d+)", contenido)

        if m_modo:
            modo = m_modo.group(1)
        elif m_prio:
            prioridades.append((m_prio.group(1), m_prio.group(2)))

    return {"modo": modo, "prioridades": prioridades}


def mostrar_identidad(nombre, datos_switch):
    version = parsear_version_ios(datos_switch["lineas"])
    print(f"Hostname     : {nombre}")
    print(f"Modelo       : {datos_switch['modelo']}")
    print(f"Numero serie : {datos_switch['serial']}")
    print(f"Version IOS  : {version}")


def mostrar_vlans(datos_switch):
    if not datos_switch["vlans"]:
        print("Sin VLANs configuradas.")
        return

    for numero, nombre_vlan in datos_switch["vlans"]:
        print(f"  VLAN {numero:<5} {nombre_vlan}")


def mostrar_puertos(lineas):
    puertos = parsear_puertos(lineas)
    if not puertos:
        print("Sin puertos configurados.")
        return

    for p in puertos:
        estado = "up" if p["up"] else "administratively down"
        print(f"\n{p['nombre']}  [{estado}]")
        print(f"  Modo         : {p['modo'] or 'no definido (access por defecto)'}")
        if p["vlan_access"]:
            print(f"  VLAN access  : {p['vlan_access']}")
        if p["vlan_trunk"]:
            print(f"  VLANs trunk  : {p['vlan_trunk']}")
        if p["descripcion"]:
            print(f"  Descripcion  : {p['descripcion']}")
        if p["duplex"]:
            print(f"  Duplex       : {p['duplex']}")
        if p["velocidad"]:
            print(f"  Velocidad    : {p['velocidad']}")


def mostrar_trunking(lineas):
    puertos = parsear_puertos(lineas)
    trunks = [p for p in puertos if p["modo"] == "trunk" or p["vlan_trunk"]]

    if not trunks:
        print("Sin puertos trunk configurados.")
        return

    for p in trunks:
        print(f"\n{p['nombre']}")
        print(f"  VLANs permitidas: {p['vlan_trunk'] or 'todas (default)'}")


def mostrar_seguridad(lineas):
    seguridad = parsear_seguridad(lineas)

    print(f"Enable secret   : {seguridad['enable_secret'] or 'no configurado'}")
    print(f"Enable password : {seguridad['enable_password'] or 'no configurado'}")
    print(f"Password consola: {seguridad['con_password'] or 'no configurada'}")
    print(f"Password VTY    : {seguridad['vty_password'] or 'no configurada'}")
    print(f"Login en VTY    : {'si' if seguridad['vty_login'] else 'no'}")

    if seguridad["port_security"]:
        print("\nPort-security configurado:")
        for interfaz, linea in seguridad["port_security"]:
            print(f"  {interfaz}: {linea}")
    else:
        print("\nSin port-security configurado.")


def mostrar_spanning_tree(lineas):
    st = parsear_spanning_tree(lineas)
    print(f"Modo: {st['modo'] or 'no configurado'}")

    if st["prioridades"]:
        print("\nPrioridades por VLAN:")
        for vlan, prioridad in st["prioridades"]:
            print(f"  VLAN {vlan}: prioridad {prioridad}")
    else:
        print("\nSin prioridades personalizadas por VLAN.")


def mostrar_config_raw(lineas):
    print("\n".join(lineas))


def mostrar_todo(nombre, datos_switch):
    print("\n=== IDENTIDAD Y HARDWARE ===")
    mostrar_identidad(nombre, datos_switch)
    print("\n=== VLANS ===")
    mostrar_vlans(datos_switch)
    print("\n=== PUERTOS ===")
    mostrar_puertos(datos_switch["lineas"])
    print("\n=== TRUNKING ===")
    mostrar_trunking(datos_switch["lineas"])
    print("\n=== SEGURIDAD ===")
    mostrar_seguridad(datos_switch["lineas"])
    print("\n=== SPANNING-TREE ===")
    mostrar_spanning_tree(datos_switch["lineas"])
    print("\n=== CONFIG COMPLETO (RAW) ===")
    mostrar_config_raw(datos_switch["lineas"])


MENU = """
1. Identidad y hardware
2. VLANs
3. Puertos
4. Trunking
5. Seguridad
6. Spanning-tree
7. Config completo (raw)
8. Todo
0. Volver
"""


def menu_switch(nombre, datos_switch):
    while True:
        print(MENU)
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            return
        elif opcion == "1":
            print()
            mostrar_identidad(nombre, datos_switch)
        elif opcion == "2":
            print()
            mostrar_vlans(datos_switch)
        elif opcion == "3":
            print()
            mostrar_puertos(datos_switch["lineas"])
        elif opcion == "4":
            print()
            mostrar_trunking(datos_switch["lineas"])
        elif opcion == "5":
            print()
            mostrar_seguridad(datos_switch["lineas"])
        elif opcion == "6":
            print()
            mostrar_spanning_tree(datos_switch["lineas"])
        elif opcion == "7":
            print()
            mostrar_config_raw(datos_switch["lineas"])
        elif opcion == "8":
            mostrar_todo(nombre, datos_switch)
        else:
            print("Opcion invalida.")
        print()


def main():
    ruta_xml = encontrar_xml()
    switches = parsear_switches(ruta_xml)

    if not switches:
        print("No se encontraron switches en el archivo XML.")
        return

    print(f"Switches disponibles: {', '.join(switches.keys())}")
    print("Escribí 'salir' para salir.\n")

    while True:
        nombre = input("Switch: ").strip()
        if nombre.lower() == "salir":
            break

        coincidencia = next((s for s in switches if s.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontro el switch '{nombre}'. Disponibles: {', '.join(switches.keys())}\n")
            continue

        menu_switch(coincidencia, switches[coincidencia])


if __name__ == "__main__":
    main()
