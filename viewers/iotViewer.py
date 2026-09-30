try:
    from viewers import generico
except ImportError:  # al correrlo directo: py viewers/iotViewer.py
    import generico

TIPOS = (
    "MCU-PT",
    "SBC-PT",
    "Sensor",
    "Actuator",
    "Thing",
    "Home Gateway",
)

mostrar_todo = generico.mostrar_todo
menu_dispositivo = generico.menu_dispositivo


def parsear_dispositivos(ruta_xml):
    return generico.parsear_dispositivos(ruta_xml, TIPOS, "Dispositivo IoT")


if __name__ == "__main__":
    generico.main(parsear_dispositivos, "No se encontraron dispositivos IoT en el archivo XML.")
