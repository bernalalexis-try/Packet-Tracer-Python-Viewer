try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/repeaterViewer.py
    import generico

TIPOS = ("Repeater",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "Repeater")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo Repeater en el archivo XML.")
