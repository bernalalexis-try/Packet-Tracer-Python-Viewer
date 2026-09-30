try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/tvViewer.py
    import generico

TIPOS = ("TV",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "TV")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo TV en el archivo XML.")
