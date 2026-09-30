try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/dslModemViewer.py
    import generico

TIPOS = ("DSL Modem",)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "DSL Modem")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos de tipo DSL Modem en el archivo XML.")
