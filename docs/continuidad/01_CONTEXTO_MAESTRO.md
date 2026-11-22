# CONTEXTO MAESTRO — ANUBIS MAG

**Fecha de corte documental:** 22 de noviembre de 2026  
**Proyecto documentado en este repositorio:** ANUBIS MAG TACTICAL

## 1. Enlaces y entorno
- Repositorio: https://github.com/pumanubis/anubis-mag-tactical
- Rama habitual: `main`
- Aplicación publicada: https://pumanubis.github.io/anubis-mag-tactical/
- Parámetro de versión usado durante pruebas recientes: `?v=80` (puede estar desactualizado; comprobar el despliegue actual).
- Proyecto Supabase asociado conocido: `qpdbswjjlpgczpubefst`
- Usuario administrador de la aplicación: `anubispuma`
- Acceso de jugadores: PIN de 4 dígitos, según el diseño solicitado.

## 2. Propósito y separación de productos
El objetivo es construir herramientas de apoyo a partidas de airsoft/MILSIM para ANUBIS MAG. Los tres productos son independientes:
1. **TACTICAL** — mapa táctico, equipos, objetivos y funciones integradas.
2. **RESPAWN** — control de respawn, vidas, alarma y QR.
3. **MISSIONS** — administración y seguimiento de misiones.

No asumir que comparten la misma base de código o despliegue. No mover funciones de un proyecto a otro ni fusionarlos sin permiso explícito.

## 3. Identidad visual y experiencia
- Estética militar, verde oliva/oscuro, negro y detalles dorados.
- Mantener el logo ANUBIS MAG existente.
- Priorizar una interfaz móvil clara, controles grandes y poco texto innecesario.
- No permitir que mapas, brújula, banners ni accesos rápidos tapen botones funcionales.
- Proteger las funciones que ya trabajan: corregir de forma localizada, evitando reescrituras grandes sin necesidad.

## 4. Equipos y jugadores
- Se admiten de 2 a 4 equipos.
- Nombres preferidos: **ALPHA, BRAVO, ECHO y DELTA**.
- Al crear una partida, se define la cantidad de equipos; el nombre del equipo se elige en el flujo de jugadores.
- Cada jugador debe ver el contexto que corresponde a su propio equipo cuando así lo establece la partida.
- En el listado administrativo, los jugadores deben agruparse por equipo y ordenarse alfabéticamente dentro de cada equipo.
- Se ha trabajado en reutilizar operadores existentes al crear partidas nuevas.
- El usuario pidió conservar el comportamiento original de Editar y Retirar/Eliminar jugadores. No cambiarlo sin permiso explícito. En partidas finalizadas, las acciones se ocultan o bloquean; la regla documentada es reabrir la partida antes de editar o retirar.
- Si un operador participa en otras partidas, el sistema puede restringir cambiar su nombre de usuario; la interfaz debe explicar esa limitación en vez de fallar silenciosamente.

## 5. Mapa, GPS y objetivos
- Mapa satelital con ubicación GPS y brújula visible bajo el mapa.
- El mapa debe centrarse en la ubicación actual del usuario cuando sea posible, no abrir mostrando toda Colombia.
- Los objetivos se pueden ordenar y deben desbloquearse según la secuencia configurada.
- Al completar/capturar un objetivo, este debe desaparecer para todos cuando así está definido por la lógica actual.
- Se busca combinar GPS, objetos 3D realistas de realidad aumentada y QR como alternativa cuando GPS/AR no resulte adecuado.
- Los administradores deben poder ubicar objetivos y objetos sobre el mapa/planos de la partida.
- Verificar siempre la implementación real antes de afirmar que todas estas capacidades están funcionando en producción.

## 6. Objetivo móvil con temporizador y sonido
Se diseñó un módulo de objetivo móvil independiente dentro de TACTICAL:
- Puede mostrarse a los dos equipos con coordenadas en tiempo real antes de activarse.
- Se activa desde el dispositivo del objetivo, sin necesidad de escanear QR para activarlo.
- Duraciones configurables: 20, 30, 40, 50 o 60 minutos.
- Emite pitidos periódicos diferenciados del sonido de respawn.
- Al llegar a cero, deben detenerse GPS y sonido.
- El flujo de desbloqueo se ha descrito así: al completar el objetivo anterior, se habilita el objetivo móvil para ambos equipos; al terminar el temporizador, se habilita el siguiente objetivo.
- Limitación conocida: una PWA en un teléfono puede no mantener GPS y audio de forma fiable con la pantalla bloqueada, debido a restricciones del sistema operativo/navegador. No prometer funcionamiento en segundo plano sin pruebas en dispositivos reales.

## 7. Accesos rápidos en móvil
Se han añadido accesos rápidos para pantallas táctiles en orientación horizontal, entre ellos “MAPA GPS” y “RESPAWN”. El acceso a respawn pretende desplazarse al control de activación; comprobar la implementación actual antes de tocarla.

## 8. Estado de la restauración de controles
Se restauró el comportamiento original de los controles de edición y retirada de jugadores, conservando la agrupación por equipo. La última referencia registrada en las notas de trabajo fue el commit `36795a18cca60583693306d9ee309de332f0f794`, pero el estado actual de la rama debe comprobarse en GitHub antes de cualquier intervención.

También se indicó que se restauró la función SQL `public.tactical_manage_player(uuid,uuid,uuid,text,uuid,text)` a la semántica anterior y se volvió a desplegar la Edge Function `admin-manage-player` sin el argumento adicional `p_callsign`. Verificar estado actual en Supabase antes de ejecutar otra migración o despliegue.

## 9. Otros proyectos relacionados

### RESPAWN ANUBIS MAG
- PWA independiente con soporte en línea y sin conexión.
- Flujo con QR para cargar partida/identificar jugador.
- Vidas ilimitadas por defecto y opción de configurar vidas limitadas.
- Temporizador de respawn y alarma.
- Logo ANUBIS MAG MILSIM verde militar/negro/dorado; no usar fondo blanco y no tapar controles.
- Se habían trabajado versiones alrededor de V6/V7; no asumir que esa es la versión actual.

### ANUBIS MAG MISSIONS
- Proyecto separado y orientado a mantener servicios gratuitos cuando sea viable.
- Asignación manual y automática de misiones, preparación antes de la partida y ajustes durante ella.
- Acceso de jugador mediante QR personal o código de jugador + clave.
- Importación de guiones desde Word/PDF como objetivo del proyecto.
- Mapas GPS y planos personalizados; objetivos visibles, desbloqueables o secretos.
- Administración desde PC o móvil con administrador principal y secundarios, evitando exigir correo al operador cuando sea posible.
- Funciones de realidad aumentada/QR contempladas como evolución futura.
- La integración con Supabase estaba en curso; verificar repositorio, proyecto y estado antes de continuar.

## 10. Principio de continuidad
Los documentos describen decisiones e historial conocido, no garantizan que el despliegue actual coincida con ellas. En cada sesión nueva:
1. Revisar el último commit de la rama.
2. Leer el archivo afectado antes de modificarlo.
3. Comprobar despliegues/validaciones.
4. Proponer el cambio mínimo necesario.
5. Probar sintaxis y flujo afectado.
6. Confirmar el resultado con evidencia y registrar el cambio.
