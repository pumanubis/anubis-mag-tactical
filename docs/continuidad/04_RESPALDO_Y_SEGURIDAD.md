# RESPALDO Y SEGURIDAD — ANUBIS MAG

## Respaldo recomendado
Mantener al menos tres copias:
1. **GitHub**: código fuente e historial de commits.
2. **ZIP local**: descargar el repositorio completo desde GitHub periódicamente.
3. **Copia de documentación**: conservar este directorio de continuidad fuera del repositorio también.

## Cómo descargar el código
1. Abrir https://github.com/pumanubis/anubis-mag-tactical
2. Pulsar **Code**.
3. Elegir **Download ZIP**.
4. Guardar el archivo con fecha, por ejemplo `anubis-mag-tactical-respaldo-AAAA-MM-DD.zip`.
5. No sobrescribir la única copia anterior hasta comprobar que el nuevo ZIP abre correctamente.

## Datos que NO deben incluirse en respaldos compartidos
- Contraseñas de administradores o jugadores.
- Claves secretas de Supabase, especialmente `service_role`.
- Tokens de GitHub, códigos de autenticación y cookies de sesión.
- Datos personales de jugadores que no sean necesarios.

El ID público del proyecto Supabase puede ayudar a identificar el entorno, pero no reemplaza las credenciales y no debe confundirse con una clave de acceso.

## Supabase: antes de modificar
- Confirmar que se está conectado al proyecto correcto.
- Revisar tablas, políticas RLS, funciones SQL, Edge Functions y migraciones existentes.
- Exportar/respaldar datos relevantes antes de migraciones destructivas.
- No ejecutar `DROP`, truncados ni reinicializaciones sin autorización expresa y respaldo verificado.
- Nunca copiar una clave secreta en un chat nuevo ni en GitHub.
- Si se necesita una clave, usar el panel seguro de Supabase o el gestor de secretos de despliegue; no pedir al usuario que la pegue en la conversación.

## Al finalizar un cambio
Registrar el commit o migración, las pruebas realizadas y lo que aún requiere prueba manual en el dispositivo real.
