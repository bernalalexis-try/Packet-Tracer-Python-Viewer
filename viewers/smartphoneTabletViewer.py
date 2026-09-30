try:
    from viewers import pcViewer
except ImportError:  # al correrlo directo: py viewers/smartphoneTabletViewer.py
    import pcViewer

TIPOS = ("Smart Phone", "Tablet PC")

parsear_leases_dhcp = pcViewer.parsear_leases_dhcp
mostrar_todo = pcViewer.mostrar_todo
menu_host = pcViewer.menu_host


def parsear_hosts(ruta_xml):
    return pcViewer.parsear_hosts(ruta_xml, TIPOS, "Dispositivo")


if __name__ == "__main__":
    pcViewer.main(
        parsear_hosts,
        "No se encontraron Smartphones ni Tablets en el archivo XML.",
        "Dispositivos",
        "Smartphone/Tablet: ",
    )
