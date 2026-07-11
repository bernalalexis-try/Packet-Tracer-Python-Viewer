# Router & Switch Viewer

Herramienta que lee archivos de topología de Cisco Packet Tracer (.xml, descifrados previamente) y extrae información de los dispositivos de red: routers y switches. Basado en el trabajo de descifrado de [Punkcake21/Unpacket](https://github.com/Punkcake21/Unpacket.git).

## Uso

1. Descifrá tu archivo `.pkt` a `.xml` usando [Unpacket](https://github.com/Punkcake21/Unpacket.git):
   py unpacket.py tu_proyecto.pkt -o tu_proyecto.xml

2. Colocá `main.py`, `routerViewer.py`, `switchViewer.py` y el `.xml` generado, todos en la misma carpeta.

3. Ejecutá:
   py main.py

4. Elegí `1` para ver routers o `2` para ver switches. Escribí `volver` para regresar al menú principal, o `0` para salir del programa.

También podés ejecutar `routerViewer.py` o `switchViewer.py` por separado si solo necesitás uno de los dos.

## Qué se puede hacer con un router

1. **Identidad y hardware**: ver hostname, modelo, número de serie y versión de IOS.

2. **Interfaces**: ver nombre, IP, máscara, estado (up/down/shutdown), descripción, VLAN (dot1Q), duplex, velocidad y MTU de cada interfaz.

3. **Ruteo**: ver la tabla de rutas estilo `show ip route` (conectadas, locales y estáticas) y el listado de rutas estáticas configuradas.

4. **Seguridad**: ver enable secret/password, contraseñas de consola y VTY, estado de login y ACLs configuradas.

5. **Red (VLANs / NAT / DHCP)**: ver subinterfaces y VLANs, reglas NAT y pools DHCP.

6. **Protocolos de enrutamiento dinámico**: ver procesos OSPF/EIGRP configurados, router ID y redes anunciadas.

7. **HSRP/VRRP**: ver grupos de redundancia de gateway configurados por interfaz (IP virtual, prioridad, preempt).

8. **Config completo (raw)**: ver el `running-config` textual completo, sin parsear.

9. **Todo**: mostrar las 8 secciones anteriores juntas, de una sola vez.

## Qué se puede hacer con un switch

1. **Identidad y hardware**: ver hostname, modelo, número de serie y versión de IOS.

2. **VLANs**: ver la base de datos completa de VLANs (número y nombre).

3. **Puertos**: ver cada interfaz con su modo (access/trunk), VLAN asignada o VLANs permitidas, estado, descripción, duplex y velocidad.

4. **Trunking**: ver específicamente qué puertos están en modo trunk y qué VLANs tienen permitidas.

5. **Seguridad**: ver enable secret/password, contraseñas de consola y VTY, y configuración de port-security por puerto.

6. **Spanning-tree**: ver el modo configurado (PVST, Rapid-PVST) y prioridades personalizadas por VLAN.

7. **Config completo (raw)**: ver el `running-config` textual completo, sin parsear.

8. **Todo**: mostrar las 7 secciones anteriores juntas, de una sola vez.
