import sys

import routerViewer
import switchViewer
import pcViewer
import serverViewer
import accessPointViewer


def flujo_dispositivo(nombre_categoria, dispositivos, prompt, menu_func):
    if not dispositivos:
        print(f"No se encontraron {nombre_categoria} en el archivo XML.\n")
        return

    print(f"\n{nombre_categoria} disponibles: {', '.join(dispositivos.keys())}")
    print("Escribí 'volver' para regresar al menú principal.\n")

    while True:
        nombre = input(prompt).strip()
        if nombre.lower() == "volver":
            break

        coincidencia = next((d for d in dispositivos if d.lower() == nombre.lower()), None)
        if coincidencia is None:
            print(f"No se encontró '{nombre}'. Disponibles: {', '.join(dispositivos.keys())}\n")
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

    while True:
        print("""
1. Routers
2. Switches
3. PCs / Laptops
4. Servers
5. Access Points
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
        else:
            print("Opción inválida.\n")


if __name__ == "__main__":
    main()
