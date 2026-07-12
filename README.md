# Router & Switch Viewer

Herramienta que lee archivos de topología de Cisco Packet Tracer (.xml, descifrados previamente) y extrae información de los dispositivos de red: routers, switches, PCs/Laptops y servers. Basado en el trabajo de descifrado de [Punkcake21/Unpacket](https://github.com/Punkcake21/Unpacket.git).

## Uso

1. Descifrá tu archivo `.pkt` a `.xml` usando [Unpacket](https://github.com/Punkcake21/Unpacket.git):
   ```
   py unpacket.py tu_proyecto.pkt -o tu_proyecto.xml
   ```
2. Colocá `main.py`, `routerViewer.py`, `switchViewer.py`, `pcViewer.py`, `serverViewer.py`, `accessPointViewer.py` y el `.xml` generado, todos en la misma carpeta.
3. Ejecutá:
   ```
   py main.py
   ```
4. Elegí `1` (routers), `2` (switches), `3` (PCs/Laptops), `4` (servers) o `5` (access points). Escribí `volver` para regresar al menú principal, o `0` para salir del programa.

También podés ejecutar cualquiera de los viewers por separado si solo necesitás uno.

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

2. **Configuración de red**: si usa DHCP, muestra la IP realmente asignada cruzando la MAC con los leases de los servidores DHCP de la topología (pool y servidor incluidos); si es estática, muestra IP, máscara, gateway y DNS configurados.

3. **Todo**: ambas secciones juntas.

## Qué se puede hacer con un Server

1. **Identidad y hardware**: hostname, modelo y número de serie.

2. **Configuración de red**: IP, máscara, gateway, DNS y MAC.

3. **Servicios habilitados**: resumen de qué servicios están activos (DHCP, DNS, HTTP, FTP, SMTP, POP3).

4. **DHCP**: pools configurados (red, gateway, DNS, rango, máximo de usuarios, cantidad de leases activos).

5. **DNS**: registros de la base de datos de nombres (tipo, nombre, IP, TTL).

6. **HTTP**: estado del servicio y credenciales si tiene autenticación.

7. **FTP**: cuentas de usuario configuradas (usuario, password, permisos).

8. **Email**: estado de SMTP/POP3, dominio y cantidad de usuarios.

9. **Todo**: las 8 secciones juntas.

## Qué se puede hacer con un Access Point

1. **Identidad y hardware**: hostname, modelo y número de serie.

2. **Configuración de red**: MAC del puerto Ethernet y MAC del puerto inalámbrico.

3. **Red inalámbrica**: SSID, modo de red (802.11b/g/n, etc.), canal, difusión de SSID y filtro de MAC.

4. **Seguridad**: código de cifrado/autenticación configurado y la clave de red (si tiene).

5. **Todo**: las 4 secciones juntas.
