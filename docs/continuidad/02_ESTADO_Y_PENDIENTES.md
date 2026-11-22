# ESTADO Y PENDIENTES — ANUBIS MAG

**Corte documental:** 22 de noviembre de 2026. Este archivo es una guía de traspaso, no una verificación en tiempo real.

## TACTICAL — comprobar primero
### Decisiones que deben preservarse
- TACTICAL sigue separado de RESPAWN y MISSIONS.
- No cambiar el flujo original de Editar/Retirar jugadores sin autorización.
- Conservar agrupación alfabética de jugadores por equipo.
- No cambiar la lógica de equipos, objetivos, login o respawn al arreglar una incidencia no relacionada.
- No asumir que una acción de GitHub/Supabase terminó: comprobar estado final.

### Verificaciones iniciales en la próxima sesión
- [ ] Revisar el commit más reciente de `main`.
- [ ] Comprobar el estado de GitHub Actions/Pages y la versión que realmente carga la URL publicada.
- [ ] Abrir la aplicación en PC y móvil; confirmar inicio de sesión de administrador y jugador.
- [ ] Verificar creación de partida, cantidad de equipos, alta/reutilización de operador y listado agrupado por equipo.
- [ ] Verificar Editar/Retirar en partida activa y comportamiento en partida finalizada.
- [ ] Verificar mapa GPS, brújula, objetivos y acceso rápido a Respawn en móvil horizontal.
- [ ] Revisar el estado real de Supabase y de la Edge Function antes de hacer cambios de backend.
- [ ] Registrar fallos reproducibles con dispositivo, navegador, pasos y resultado esperado/real.

### Historial técnico conocido que requiere comprobación
- Hubo un error de sintaxis en una versión anterior de `index.html` que afectó el acceso; se corrigió y luego se restauraron los controles originales.
- El commit documentado para restaurar Editar/Retirar y conservar agrupación por equipo fue `36795a18cca60583693306d9ee309de332f0f794`.
- En el momento de la nota, la validación de ese commit figuraba como exitosa, pero el despliegue de Pages aún aparecía en curso. Consultar estado actual; no dar por hecho que se publicó.
- La base de datos y la Edge Function se habían ajustado para quitar el argumento extra `p_callsign`; confirmar el estado actual antes de tocar el esquema.

## RESPAWN — proyecto independiente
- [ ] Localizar su repositorio/código vigente y registrar URL y commit.
- [ ] Confirmar qué versión está publicada e instalada en los teléfonos.
- [ ] Probar QR, modo sin conexión, alarma, temporizador y descuento de vidas.
- [ ] Mantener logo y controles sin superposición.

## MISSIONS — proyecto independiente
- [ ] Localizar repositorio, URL publicada y proyecto Supabase correcto.
- [ ] Revisar el JSON de respaldo exportado por el usuario si está disponible en la sesión o en sus archivos.
- [ ] Identificar qué tablas, políticas, funciones y despliegues ya existen antes de ejecutar SQL.
- [ ] Confirmar acceso de administrador principal/secundarios y login de jugador.
- [ ] No borrar ni reinicializar datos para “empezar de cero” sin autorización.

## Registro de cada intervención
Para cada cambio, documentar:
- Fecha y hora.
- Proyecto y archivo/función modificada.
- Problema que se corrige.
- Cambio mínimo realizado.
- Validaciones ejecutadas y resultado.
- Commit, migración o despliegue resultante.
- Qué falta probar manualmente.
