# Router & Switch Viewer

Herramienta que lee archivos de topología de Cisco Packet Tracer (.xml, descifrados previamente) y extrae información de los dispositivos de red: routers, switches, PCs/Laptops, servers, access points, hubs, bridges, firewalls, clouds, DSL modems, power distribution devices, cable modems, home wireless routers, repeaters, printers, IP phones, TVs, smartphones/tablets y dispositivos IoT. Basado en el trabajo de descifrado de [Punkcake21/Unpacket](https://github.com/Punkcake21/Unpacket.git).

## Uso

1. Descifrá tu archivo `.pkt` a `.xml` usando [Unpacket](https://github.com/Punkcake21/Unpacket.git):
   ```
   py unpacket.py tu_proyecto.pkt -o tu_proyecto.xml
   ```
2. Colocá `main.py` y el `.xml` generado en la raíz del proyecto, junto a la carpeta `viewers/`.
3. Ejecutá:
   ```
   py main.py
   ```
4. Elegí una categoría (`1` al `19`), después elegí el dispositivo por número o escribiendo su nombre. `0` siempre vuelve al paso anterior; desde el listado de dispositivos también volvés al menú principal escribiendo `volver`.

También podés ejecutar cualquiera de los viewers por separado si solo necesitás uno (por ejemplo, `py viewers/routerViewer.py`).

## Qué se puede hacer con un router

1. **Identidad y hardware**: hostname, modelo, número de serie y versión de IOS.

2. **Interfaces**: nombre, IP, máscara, estado (up/down/shutdown), descripción, VLAN (dot1Q), duplex, velocidad y MTU.

3. **Ruteo**: tabla de rutas estilo `show ip route` (conectadas, locales y estáticas) y rutas estáticas configuradas.

4. **Seguridad**: enable secret/password, contraseñas de consola y VTY, estado de login y ACLs.

5. **Red (VLANs / NAT / DHCP)**: subinterfaces y VLANs, reglas NAT y pools DHCP.
6. **Protocolos de enrutamiento dinámico**: procesos OSPF/EIGRP, router ID y redes anunciadas.

7. **HSRP/VRRP**: grupos de redundancia de gateway por interfaz (IP virtual, prioridad, preempt).

8. **Config completo (raw)**: `running-config` textual completo, sin parsear.

9. **Todo**: las 8 secciones juntas.

## Qué se puede hacer con un switch

1. **Identidad y hardware**: hostname, modelo, número de serie y versión de IOS.

2. **VLANs**: base de datos completa de VLANs (número y nombre).

3. **Puertos**: modo (access/trunk), VLAN asignada o permitidas, estado, descripción, duplex y velocidad.

4. **Trunking**: puertos en modo trunk y VLANs permitidas.

5. **Seguridad**: enable secret/password, contraseñas de consola/VTY, port-security por puerto.

6. **Spanning-tree**: modo configurado (PVST, Rapid-PVST) y prioridades por VLAN.

7. **Config completo (raw)**: `running-config` textual completo, sin parsear.

8. **Todo**: las 7 secciones juntas.

## Qué se puede hacer con una PC/Laptop

1. **Identidad**: nombre, tipo (Pc/Laptop) y dirección MAC.

2. **Configuración de red**: IP asignada por DHCP cruzando la MAC con los leases de los servidores DHCP de la topología (pool y servidor incluidos), o IP, máscara, gateway y DNS estáticos.

3. **Todo**: ambas secciones juntas.

## Qué se puede hacer con un Server

1. **Identidad y hardware**: hostname, modelo y número de serie.

2. **Configuración de red**: IP, máscara, gateway, DNS y MAC.

3. **Servicios habilitados**: resumen de qué servicios están activos (DHCP, DNS, HTTP, FTP, SMTP, POP3).

4. **DHCP**: pools configurados (red, gateway, DNS, rango, máximo de usuarios, cantidad de leases activos).

5. **DNS**: registros de la base de datos de nombres (tipo, nombre, IP, TTL).

6. **HTTP**: estado del servicio y credenciales de autenticación.

7. **FTP**: cuentas de usuario configuradas (usuario, password, permisos).

8. **Email**: estado de SMTP/POP3, dominio y cantidad de usuarios.

9. **Todo**: las 8 secciones juntas.

## Qué se puede hacer con un Access Point

1. **Identidad y hardware**: hostname, modelo y número de serie.

2. **Configuración de red**: MAC del puerto Ethernet y MAC del puerto inalámbrico.

3. **Red inalámbrica**: SSID, modo de red (802.11b/g/n, etc.), canal, difusión de SSID y filtro de MAC.

4. **Seguridad**: código de cifrado/autenticación configurado y la clave de red.

5. **Todo**: las 4 secciones juntas.

## Qué se puede hacer con Hub, Bridge, Firewall, Cloud, DSL Modem y Power Distribution Device

Cada uno tiene su propio viewer (`hubViewer.py`, `bridgeViewer.py`, `firewallViewer.py`, `cloudViewer.py`, `dslModemViewer.py`, `powerDistributionDeviceViewer.py`), todos con el mismo menú:

1. **Identidad y hardware**: nombre, tipo, modelo, número de serie y estado de encendido.

2. **Puertos**: direcciones MAC de los puertos del dispositivo.

3. **Atributos físicos**: consumo (wattage), unidades de rack, MTBF, costo y fuente de alimentación.

4. **Config completo (raw)**: `running-config` textual completo, sin parsear.

5. **Todo**: las 4 secciones juntas.

## Qué se puede hacer con Cable Modem, Home Wireless Router, Repeater, Printer, IP Phone y TV

Cada uno tiene su propio viewer (`cableModemViewer.py`, `homeWirelessRouterViewer.py`, `repeaterViewer.py`, `printerViewer.py`, `ipPhoneViewer.py`, `tvViewer.py`), con el mismo menú que Hub/Bridge/Firewall/Cloud/DSL Modem/Power Distribution Device: identidad y hardware, puertos, atributos físicos, config completo y todo junto.

## Qué se puede hacer con Smartphone/Tablet

`smartphoneTabletViewer.py` funciona igual que el de PC/Laptop: identidad (nombre, tipo y MAC) y configuración de red (IP asignada por DHCP cruzando la MAC con los leases de los servidores, o IP estática).

## Qué se puede hacer con dispositivos IoT

`iotViewer.py` agrupa microcontroladores (MCU), sensores, actuadores y otros componentes IoT bajo el mismo menú que los dispositivos genéricos: identidad y hardware, puertos, atributos físicos, config completo y todo junto.