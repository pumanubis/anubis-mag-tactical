# Respawn en ANUBIS MAG TACTICAL

El módulo aparece al final de la pantalla del jugador, debajo del mapa y de los demás controles. Incluye cronómetro (1 minuto de forma predeterminada), regreso a base por QR, vidas configurables, partidas preparadas y desbloqueo de emergencia de Respawn.

## Uso

- El organizador genera los dos QR en el panel de administración de Respawn. Debe conservar y reutilizar la misma credencial cifrada para las siguientes partidas.
- En el teléfono, abre Tactical con internet y toca «Cargar partida (QR)» para escanear el QR 1 de configuración. Prepara el uso sin conexión con «Activar offline» antes de salir a jugar.
- En modo base, inicia el respawn y escanea el QR 2 de esa misma partida. Un QR incorrecto no termina el respawn.
- El módulo mantiene sus propios QR y su estado local por navegador. No escribe partidas, usuarios ni capturas de Tactical, ni comparte datos con la aplicación independiente de Respawn. Tampoco impide capturar objetivos de Tactical.

El respaldo previo a la integración está en la rama `tactical-v70-antes-de-respawn`.

Origen del módulo: `pumanubis/respawn-anubis-mag`, commit `e5e613726d59819007fc706114ad1c334e5d317e`.
