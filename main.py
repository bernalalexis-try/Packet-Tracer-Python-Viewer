import argparse
import contextlib
import io
import sys

from viewers import (
    accessPointViewer,
    bridgeViewer,
    cableModemViewer,
    cloudViewer,
    dslModemViewer,
    firewallViewer,
    homeWirelessRouterViewer,
    hubViewer,
    iotViewer,
    ipPhoneViewer,
    pcViewer,
    powerDistributionDeviceViewer,
    printerViewer,
    repeaterViewer,
    routerViewer,
    serverViewer,
    smartphoneTabletViewer,
    switchViewer,
    tvViewer,
)
from viewers.comun import encontrar_xml


def cargar_categorias(ruta_xml):
    """Parsea el XML y devuelve (titulo, prompt, dispositivos, menu, todo) por categoría."""
    leases = pcViewer.parsear_leases_dhcp(ruta_xml)

    def con_leases(funcion):
        return lambda nombre, datos: funcion(nombre, datos, leases)

    categorias = [
        ("Routers", "Router", routerViewer.parsear_routers, routerViewer.menu_router, routerViewer.mostrar_todo),
        ("Switches", "Switch", switchViewer.parsear_switches, switchViewer.menu_switch, switchViewer.mostrar_todo),
        (
            "PCs / Laptops", "PC/Laptop", pcViewer.parsear_hosts,
            con_leases(pcViewer.menu_host), con_leases(pcViewer.mostrar_todo),
        ),
        ("Servers", "Server", serverViewer.parsear_servers, serverViewer.menu_server, serverViewer.mostrar_todo),
        (
            "Access Points", "Access Point", accessPointViewer.parsear_access_points,
            accessPointViewer.menu_ap, accessPointViewer.mostrar_todo,
        ),
        ("Hubs", "Hub", hubViewer.parsear_dispositivos, hubViewer.menu_dispositivo, hubViewer.mostrar_todo),
        ("Bridges", "Bridge", bridgeViewer.parsear_dispositivos, bridgeViewer.menu_dispositivo, bridgeViewer.mostrar_todo),
        (
            "Firewalls", "Firewall", firewallViewer.parsear_dispositivos,
            firewallViewer.menu_dispositivo, firewallViewer.mostrar_todo,
        ),
        ("Clouds", "Cloud", cloudViewer.parsear_dispositivos, cloudViewer.menu_dispositivo, cloudViewer.mostrar_todo),
        (
            "DSL Modems", "DSL Modem", dslModemViewer.parsear_dispositivos,
            dslModemViewer.menu_dispositivo, dslModemViewer.mostrar_todo,
        ),
        (
            "Power Distribution Devices", "Power Distribution Device",
            powerDistributionDeviceViewer.parsear_dispositivos,
            powerDistributionDeviceViewer.menu_dispositivo, powerDistributionDeviceViewer.mostrar_todo,
        ),
        (
            "Cable Modems", "Cable Modem", cableModemViewer.parsear_dispositivos,
            cableModemViewer.menu_dispositivo, cableModemViewer.mostrar_todo,
        ),
        (
            "Home Wireless Routers", "Home Wireless Router", homeWirelessRouterViewer.parsear_dispositivos,
            homeWirelessRouterViewer.menu_dispositivo, homeWirelessRouterViewer.mostrar_todo,
        ),
        (
            "Repeaters", "Repeater", repeaterViewer.parsear_dispositivos,
            repeaterViewer.menu_dispositivo, repeaterViewer.mostrar_todo,
        ),
        (
            "Printers", "Printer", printerViewer.parsear_dispositivos,
            printerViewer.menu_dispositivo, printerViewer.mostrar_todo,
        ),
        (
            "IP Phones", "IP Phone", ipPhoneViewer.parsear_dispositivos,
            ipPhoneViewer.menu_dispositivo, ipPhoneViewer.mostrar_todo,
        ),
        ("TVs", "TV", tvViewer.parsear_dispositivos, tvViewer.menu_dispositivo, tvViewer.mostrar_todo),
        (
            "Smartphones / Tablets", "Smartphone/Tablet", smartphoneTabletViewer.parsear_hosts,
            con_leases(smartphoneTabletViewer.menu_host), con_leases(smartphoneTabletViewer.mostrar_todo),
        ),
        (
            "Dispositivos IoT", "Dispositivo IoT", iotViewer.parsear_dispositivos,
            iotViewer.menu_dispositivo, iotViewer.mostrar_todo,
        ),
    ]

    return [
        (titulo, prompt, parsear(ruta_xml), menu, todo)
        for titulo, prompt, parsear, menu, todo in categorias
    ]


def flujo_dispositivo(nombre_categoria, dispositivos, prompt, menu_func):
    if not dispositivos:
        print(f"No se encontraron {nombre_categoria} en el archivo XML.\n")
        return

    nombres = list(dispositivos.keys())

    while True:
        print(f"\n{nombre_categoria} disponibles:")
        for i, nombre in enumerate(nombres, start=1):
            print(f"{i}. {nombre}")
        print("0. Volver\n")

        entrada = input(prompt).strip()

        if entrada == "0" or entrada.lower() in ("volver", "salir"):
            return

        if entrada.isdigit():
            indice = int(entrada) - 1
            if 0 <= indice < len(nombres):
                menu_func(nombres[indice], dispositivos[nombres[indice]])
                continue
            print(f"No hay ninguna opción con el número '{entrada}'.\n")
            continue

        coincidencia = next((d for d in nombres if d.lower() == entrada.lower()), None)
        if coincidencia is None:
            print(f"No se encontró '{entrada}'.\n")
            continue

        menu_func(coincidencia, dispositivos[coincidencia])


def generar_reporte(categorias):
    """Devuelve en un solo texto la sección "Todo" de cada dispositivo."""
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        for titulo, _, dispositivos, _, mostrar_todo in categorias:
            if not dispositivos:
                continue
            print(f"\n{'#' * 60}\n# {titulo.upper()} ({len(dispositivos)})\n{'#' * 60}")
            for nombre, datos in dispositivos.items():
                print(f"\n----- {nombre} -----")
                mostrar_todo(nombre, datos)
    return salida.getvalue().lstrip("\n")


def exportar(categorias, ruta_salida):
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(generar_reporte(categorias))
    print(f"Reporte guardado en '{ruta_salida}'.")


def main():
    parser = argparse.ArgumentParser(description="Muestra los dispositivos de un .xml de Packet Tracer.")
    parser.add_argument("xml", nargs="?", help="archivo .xml descifrado con Unpacket")
    parser.add_argument("--exportar", metavar="ARCHIVO", help="guarda todo en un .txt y sale")
    args = parser.parse_args()

    ruta_xml = encontrar_xml(args.xml)
    categorias = cargar_categorias(ruta_xml)

    if args.exportar:
        exportar(categorias, args.exportar)
        return

    opcion_exportar = str(len(categorias) + 1)

    while True:
        print()
        for i, (titulo, _, dispositivos, _, _) in enumerate(categorias, start=1):
            print(f"{i}. {titulo} ({len(dispositivos)})")
        print(f"{opcion_exportar}. Exportar todo a un .txt")
        print("0. Salir\n")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            sys.exit(0)
        elif opcion == opcion_exportar:
            ruta_salida = input("Nombre del archivo (Enter = reporte.txt): ").strip() or "reporte.txt"
            exportar(categorias, ruta_salida)
        elif opcion.isdigit() and 1 <= int(opcion) <= len(categorias):
            titulo, prompt, dispositivos, menu, _ = categorias[int(opcion) - 1]
            flujo_dispositivo(titulo, dispositivos, f"{prompt}: ", menu)
        else:
            print("Opción inválida.\n")


if __name__ == "__main__":
    main()
