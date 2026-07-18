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


def main():
    ruta_xml = routerViewer.encontrar_xml()
    routers = routerViewer.parsear_routers(ruta_xml)
    switches = switchViewer.parsear_switches(ruta_xml)
    hosts = pcViewer.parsear_hosts(ruta_xml)
    leases = pcViewer.parsear_leases_dhcp(ruta_xml)
    servers = serverViewer.parsear_servers(ruta_xml)
    aps = accessPointViewer.parsear_access_points(ruta_xml)
    hubs = hubViewer.parsear_dispositivos(ruta_xml)
    bridges = bridgeViewer.parsear_dispositivos(ruta_xml)
    firewalls = firewallViewer.parsear_dispositivos(ruta_xml)
    clouds = cloudViewer.parsear_dispositivos(ruta_xml)
    dsl_modems = dslModemViewer.parsear_dispositivos(ruta_xml)
    pdds = powerDistributionDeviceViewer.parsear_dispositivos(ruta_xml)
    cable_modems = cableModemViewer.parsear_dispositivos(ruta_xml)
    home_routers = homeWirelessRouterViewer.parsear_dispositivos(ruta_xml)
    repeaters = repeaterViewer.parsear_dispositivos(ruta_xml)
    printers = printerViewer.parsear_dispositivos(ruta_xml)
    ip_phones = ipPhoneViewer.parsear_dispositivos(ruta_xml)
    tvs = tvViewer.parsear_dispositivos(ruta_xml)
    moviles = smartphoneTabletViewer.parsear_hosts(ruta_xml)
    moviles_leases = smartphoneTabletViewer.parsear_leases_dhcp(ruta_xml)
    iots = iotViewer.parsear_dispositivos(ruta_xml)

    while True:
        print("""
1. Routers
2. Switches
3. PCs / Laptops
4. Servers
5. Access Points
6. Hubs
7. Bridges
8. Firewalls
9. Clouds
10. DSL Modems
11. Power Distribution Devices
12. Cable Modems
13. Home Wireless Routers
14. Repeaters
15. Printers
16. IP Phones
17. TVs
18. Smartphones / Tablets
19. Dispositivos IoT
0. Salir
""")
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            sys.exit(0)
        elif opcion == "1":
            flujo_dispositivo("Routers", routers, "Router: ", routerViewer.menu_router)
        elif opcion == "2":
            flujo_dispositivo("Switches", switches, "Switch: ", switchViewer.menu_switch)
        elif opcion == "3":
            flujo_dispositivo(
                "PCs/Laptops", hosts, "PC/Laptop: ",
                lambda n, d: pcViewer.menu_host(n, d, leases),
            )
        elif opcion == "4":
            flujo_dispositivo("Servers", servers, "Server: ", serverViewer.menu_server)
        elif opcion == "5":
            flujo_dispositivo("Access Points", aps, "Access Point: ", accessPointViewer.menu_ap)
        elif opcion == "6":
            flujo_dispositivo("Hubs", hubs, "Hub: ", hubViewer.menu_dispositivo)
        elif opcion == "7":
            flujo_dispositivo("Bridges", bridges, "Bridge: ", bridgeViewer.menu_dispositivo)
        elif opcion == "8":
            flujo_dispositivo("Firewalls", firewalls, "Firewall: ", firewallViewer.menu_dispositivo)
        elif opcion == "9":
            flujo_dispositivo("Clouds", clouds, "Cloud: ", cloudViewer.menu_dispositivo)
        elif opcion == "10":
            flujo_dispositivo("DSL Modems", dsl_modems, "DSL Modem: ", dslModemViewer.menu_dispositivo)
        elif opcion == "11":
            flujo_dispositivo(
                "Power Distribution Devices", pdds, "Power Distribution Device: ",
                powerDistributionDeviceViewer.menu_dispositivo,
            )
        elif opcion == "12":
            flujo_dispositivo("Cable Modems", cable_modems, "Cable Modem: ", cableModemViewer.menu_dispositivo)
        elif opcion == "13":
            flujo_dispositivo(
                "Home Wireless Routers", home_routers, "Home Wireless Router: ",
                homeWirelessRouterViewer.menu_dispositivo,
            )
        elif opcion == "14":
            flujo_dispositivo("Repeaters", repeaters, "Repeater: ", repeaterViewer.menu_dispositivo)
        elif opcion == "15":
            flujo_dispositivo("Printers", printers, "Printer: ", printerViewer.menu_dispositivo)
        elif opcion == "16":
            flujo_dispositivo("IP Phones", ip_phones, "IP Phone: ", ipPhoneViewer.menu_dispositivo)
        elif opcion == "17":
            flujo_dispositivo("TVs", tvs, "TV: ", tvViewer.menu_dispositivo)
        elif opcion == "18":
            flujo_dispositivo(
                "Smartphones/Tablets", moviles, "Smartphone/Tablet: ",
                lambda n, d: smartphoneTabletViewer.menu_host(n, d, moviles_leases),
            )
        elif opcion == "19":
            flujo_dispositivo("Dispositivos IoT", iots, "Dispositivo IoT: ", iotViewer.menu_dispositivo)
        else:
            print("Opción inválida.\n")


if __name__ == "__main__":
    main()