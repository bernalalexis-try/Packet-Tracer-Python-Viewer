try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/homeWirelessRouterViewer.py
    import generico

TIPOS = ("Home Wireless Router",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "Home Wireless Router")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo Home Wireless Router en el archivo XML.")
