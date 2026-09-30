import contextlib
import io
import os
import tempfile
import unittest

import main
from viewers import (
    comun,
    hubViewer,
    iotViewer,
    pcViewer,
    routerViewer,
    serverViewer,
    smartphoneTabletViewer,
    switchViewer,
)

EJEMPLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplo.xml")


def salida_de(funcion, *args):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        funcion(*args)
    return buffer.getvalue()


class TestComun(unittest.TestCase):
    def test_decodifica_entidades_en_todo_el_resultado(self):
        datos = {"a&amp;b": ["x &lt;-&gt; y", ("&amp;",)], "n": 1}
        self.assertEqual(comun.decodificar(datos), {"a&b": ["x <-> y", ("&",)], "n": 1})

    def test_no_pisa_dispositivos_con_el_mismo_nombre(self):
        dispositivos = {}
        for datos in ("primero", "segundo", "tercero"):
            comun.agregar_dispositivo(dispositivos, "PC0", datos)
        self.assertEqual(dispositivos, {"PC0": "primero", "PC0 (2)": "segundo", "PC0 (3)": "tercero"})

    def test_usa_el_xml_que_se_le_pasa(self):
        self.assertEqual(comun.encontrar_xml(EJEMPLO), EJEMPLO)

    def test_sale_si_el_xml_no_existe(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            comun.encontrar_xml("no-existe.xml")


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.routers = routerViewer.parsear_routers(EJEMPLO)

    def test_routers_con_el_mismo_nombre(self):
        self.assertEqual(list(self.routers), ["R1", "R1 (2)"])

    def test_descripcion_con_caracteres_especiales(self):
        salida = salida_de(routerViewer.mostrar_todo, "R1", self.routers["R1"])
        self.assertIn("Descripcion  : LAN <-> SW1 & PCs", salida)
        self.assertNotIn("&lt;", salida)

    def test_tabla_de_rutas(self):
        salida = salida_de(routerViewer.mostrar_todo, "R1", self.routers["R1"])
        self.assertIn("C       192.168.1.0/24 is directly connected, GigabitEthernet0/0", salida)
        self.assertIn("S*    0.0.0.0/0 [1/0] via 10.0.0.2", salida)

    def test_pool_dhcp_sin_dns(self):
        salida = salida_de(routerViewer.mostrar_todo, "R1", self.routers["R1"])
        self.assertIn("dns sin configurar", salida)
        self.assertNotIn("None", salida)


class TestSwitch(unittest.TestCase):
    def test_vlans(self):
        switches = switchViewer.parsear_switches(EJEMPLO)
        self.assertEqual(switches["SW1"]["vlans"], [(1, "default"), (10, "VENTAS")])


class TestHosts(unittest.TestCase):
    def setUp(self):
        self.hosts = pcViewer.parsear_hosts(EJEMPLO)
        self.leases = pcViewer.parsear_leases_dhcp(EJEMPLO)

    def red(self, nombre):
        return salida_de(pcViewer.mostrar_red, self.hosts[nombre], self.leases)

    def test_pcs_y_laptops(self):
        self.assertEqual(list(self.hosts), ["PC-DHCP", "PC-APIPA", "LAPTOP-FIJA"])

    def test_ip_por_lease_del_servidor(self):
        salida = self.red("PC-DHCP")
        self.assertIn("IP asignada  : 192.168.1.10", salida)
        self.assertIn("Servidor DHCP: SRV-DHCP", salida)

    def test_apipa(self):
        self.assertIn("169.254.10.20 255.255.0.0 (APIPA", self.red("PC-APIPA"))

    def test_ip_estatica(self):
        salida = self.red("LAPTOP-FIJA")
        self.assertIn("Configuracion: Estatica", salida)
        self.assertIn("IP           : 192.168.1.100", salida)

    def test_smartphone(self):
        self.assertEqual(list(smartphoneTabletViewer.parsear_hosts(EJEMPLO)), ["Celu"])


class TestServer(unittest.TestCase):
    def test_pool_dhcp(self):
        servers = serverViewer.parsear_servers(EJEMPLO)
        dhcp = serverViewer.parsear_dhcp(servers["SRV-DHCP"]["bloque"])
        self.assertTrue(dhcp["habilitado"])
        self.assertEqual(dhcp["pools"][0]["nombre"], "serverPool")


class TestGenericos(unittest.TestCase):
    def test_hubs_con_el_mismo_nombre(self):
        hubs = hubViewer.parsear_dispositivos(EJEMPLO)
        self.assertEqual(list(hubs), ["Hub0", "Hub0 (2)"])
        self.assertTrue(hubs["Hub0"]["encendido"])
        self.assertFalse(hubs["Hub0 (2)"]["encendido"])
        self.assertEqual(hubs["Hub0"]["atributos"], {"wattage": "5", "rack units": "1", "cost": "100"})

    def test_iot_muestra_su_tipo(self):
        iots = iotViewer.parsear_dispositivos(EJEMPLO)
        salida = salida_de(iotViewer.mostrar_todo, "Sensor0", iots["Sensor0"])
        self.assertIn("Tipo         : Sensor", salida)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.categorias = main.cargar_categorias(EJEMPLO)

    def test_cantidades_por_categoria(self):
        cantidades = {titulo: len(dispositivos) for titulo, _, dispositivos, _, _ in self.categorias}
        self.assertEqual(cantidades["Routers"], 2)
        self.assertEqual(cantidades["PCs / Laptops"], 3)
        self.assertEqual(cantidades["Hubs"], 2)
        self.assertEqual(cantidades["Firewalls"], 0)

    def test_reporte_incluye_todos_los_dispositivos(self):
        reporte = main.generar_reporte(self.categorias)
        for nombre in ("R1", "R1 (2)", "SW1", "PC-DHCP", "SRV-DHCP", "Hub0 (2)", "Sensor0", "Celu"):
            self.assertIn(f"----- {nombre} -----", reporte)
        self.assertNotIn("# FIREWALLS", reporte)

    def test_exportar_a_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "reporte.txt")
            with contextlib.redirect_stdout(io.StringIO()):
                main.exportar(self.categorias, ruta)
            with open(ruta, encoding="utf-8") as f:
                self.assertIn("# ROUTERS (2)", f.read())


if __name__ == "__main__":
    unittest.main()
