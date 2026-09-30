try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/firewallViewer.py
    import generico

TIPOS = ("Firewall",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "Firewall")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo Firewall en el archivo XML.")
