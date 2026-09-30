try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/printerViewer.py
    import generico

TIPOS = ("Printer",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "Printer")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo Printer en el archivo XML.")
