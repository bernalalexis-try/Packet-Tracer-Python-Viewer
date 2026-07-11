import sys

import routerViewer
import switchViewer


def main():
    ruta_xml = routerViewer.encontrar_xml()
    routers = routerViewer.parsear_routers(ruta_xml)
    switches = switchViewer.parsear_switches(ruta_xml)

    while True:
        print("""
1. Routers
2. Switches
0. Salir
""")
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            sys.exit(0)

        elif opcion == "1":
            if not routers:
                print("No se encontraron routers en el archivo XML.\n")
                continue

            print(f"\nRouters disponibles: {', '.join(routers.keys())}")
            print("Escribí 'volver' para regresar al menú principal.\n")

            while True:
                nombre = input("Router: ").strip()
                if nombre.lower() == "volver":
                    break

                coincidencia = next((r for r in routers if r.lower() == nombre.lower()), None)
                if coincidencia is None:
                    print(f"No se encontró el router '{nombre}'. Disponibles: {', '.join(routers.keys())}\n")
                    continue

                routerViewer.menu_router(coincidencia, routers[coincidencia])

        elif opcion == "2":
            if not switches:
                print("No se encontraron switches en el archivo XML.\n")
                continue

            print(f"\nSwitches disponibles: {', '.join(switches.keys())}")
            print("Escribí 'volver' para regresar al menú principal.\n")

            while True:
                nombre = input("Switch: ").strip()
                if nombre.lower() == "volver":
                    break

                coincidencia = next((s for s in switches if s.lower() == nombre.lower()), None)
                if coincidencia is None:
                    print(f"No se encontró el switch '{nombre}'. Disponibles: {', '.join(switches.keys())}\n")
                    continue

                switchViewer.menu_switch(coincidencia, switches[coincidencia])

        else:
            print("Opción inválida.\n")


if __name__ == "__main__":
    main()
