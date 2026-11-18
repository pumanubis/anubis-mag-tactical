# Respawn de prueba en Tactical V70

El botón «Abrir Respawn de prueba» está disponible en el acceso a Tactical y en la pantalla de jugador de esta rama. El módulo conserva el cronómetro, regreso a base por QR, vidas, partidas preparadas y desbloqueo de emergencia de Respawn V7.3.1. Los QR y credenciales de esta prueba son exclusivos del módulo. No se consultan ni actualizan partidas, usuarios ni capturas de Tactical desde Respawn. El progreso es local a cada navegador y en esta rama no impide capturar objetivos de Tactical.

## Abrir sin publicar

1. Descarga el ZIP de la rama `prueba-respawn-v70` y descomprímelo.
2. Abre una terminal en la carpeta que contiene `index.html` y ejecuta `py -m http.server 8000 --bind 127.0.0.1` (Windows con Python). En macOS/Linux, ejecuta `python3 -m http.server 8000 --bind 127.0.0.1`.
3. Abre http://localhost:8000/respawn/ en el mismo equipo. Para probar en un celular se necesita un entorno de prueba con HTTPS. La rama no cambia GitHub Pages ni requiere un inicio de sesión de Tactical para probar Respawn.

## Prueba manual sugerida

- Inicia un cronómetro, intenta cambiar la modalidad y recarga. Debe continuar hasta el final.
- En el panel Administrador crea una credencial **de prueba**. Genera una partida y sus dos QR.
- En el celular, carga el QR de configuración antes de iniciar el modo base. Un QR incorrecto no debe finalizarlo. Escanea el de base de esa misma partida para terminar.
- Con internet, pulsa «Activar offline» antes de probar en modo avión. Deja activos el volumen y la cámara. Usa el QR de esta prueba, no el QR de la app independiente.

Origen del módulo: `pumanubis/respawn-anubis-mag`, commit `e5e613726d59819007fc706114ad1c334e5d317e`.
