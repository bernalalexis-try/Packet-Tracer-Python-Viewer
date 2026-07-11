# Router Viewer

Herramienta que lee archivos de topología de Cisco Packet Tracer (.xml, descifrados previamente) y extrae información de los dispositivos de red. Actualmente muestra información detallada de cada router, con soporte planeado para switches y otros dispositivos. Basado en el trabajo de descifrado de [Punkcake21/Unpacket](https://github.com/Punkcake21/Unpacket.git).

## Uso

1. Descifrá tu archivo `.pkt` a `.xml` usando [Unpacket](https://github.com/Punkcake21/Unpacket.git):
   py unpacket.py tu_proyecto.pkt -o tu_proyecto.xml
   
2. Colocá `routerViewer.py` en la misma carpeta que el `.xml` generado.

3. Ejecutá:
   py routerViewer.py

4. Escribí el nombre de un router para ver su menú de información. Escribí `salir` para salir del programa.

## Qué se puede hacer con un router

Al seleccionar un router, se puede elegir entre las siguientes secciones:

1. **Identidad y hardware**: ver hostname, modelo, número de serie y versión de IOS.
2. **Interfaces**: ver nombre, IP, máscara, estado (up/down/shutdown), descripción, VLAN (dot1Q), duplex, velocidad y MTU de cada interfaz.
3. **Ruteo**: ver la tabla de rutas estilo `show ip route` (conectadas, locales y estáticas) y el listado de rutas estáticas configuradas.
4. **Seguridad**: ver enable secret/password, contraseñas de consola y VTY, estado de login y ACLs configuradas.
5. **Red (VLANs / NAT / DHCP)**: ver subinterfaces y VLANs, reglas NAT y pools DHCP.
6. **Todo**: mostrar las 5 secciones anteriores juntas, de una sola vez.

**Nota:** solo soporta rutas conectadas, locales y estáticas (no protocolos de enrutamiento dinámico como OSPF o EIGRP).
