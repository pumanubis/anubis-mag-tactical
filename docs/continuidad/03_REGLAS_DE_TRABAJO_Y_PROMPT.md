# REGLAS DE TRABAJO Y PROMPT PARA OTRO CHAT

## Reglas que debe seguir el asistente
1. Responder en español, con instrucciones claras y prácticas.
2. Antes de modificar código, abrir y revisar el archivo real de la rama actual.
3. No inventar funciones, pruebas, resultados, URLs, commits ni estados de despliegue.
4. Mantener separados TACTICAL, RESPAWN y MISSIONS.
5. No reemplazar el archivo completo ni reescribir módulos grandes cuando basta un cambio localizado.
6. No quitar ni alterar una función que ya trabaja sin permiso explícito.
7. Respetar el comportamiento original de Editar/Retirar jugadores, agrupación por equipos y lógica de partidas.
8. En cambios de base de datos, revisar esquema, funciones, políticas y migraciones existentes antes de ejecutar SQL.
9. Nunca pedir ni escribir contraseñas, tokens, claves secretas o códigos de autenticación en archivos de documentación o en el repositorio.
10. Distinguir claramente entre: confirmado por el código, confirmado en producción, decisión acordada y tarea pendiente.
11. Después de cada cambio, validar sintaxis, revisar el diff y comprobar el despliegue si aplica.
12. Si no se puede comprobar algo, decirlo y pedir el dato mínimo necesario en lugar de adivinar.

## Prompt listo para copiar y pegar en un nuevo chat

Estoy continuando el proyecto ANUBIS MAG y no quiero empezar desde cero. Trabaja en español y sigue estas reglas:

- Lee primero el contexto maestro, estado y reglas de continuidad en:
  https://github.com/pumanubis/anubis-mag-tactical/tree/main/docs/continuidad
- Proyecto actual: ANUBIS MAG TACTICAL.
- Repositorio: https://github.com/pumanubis/anubis-mag-tactical
- Aplicación publicada: https://pumanubis.github.io/anubis-mag-tactical/
- Rama habitual: main.
- Proyecto Supabase conocido: qpdbswjjlpgczpubefst.
- ANUBIS MAG TACTICAL, RESPAWN ANUBIS MAG y ANUBIS MAG MISSIONS son proyectos separados. No los mezcles.
- Antes de proponer o ejecutar cambios, revisa el código vigente y el último commit; verifica el estado del despliegue.
- No alteres el comportamiento original de Editar/Retirar jugadores sin pedirme permiso. Conserva el listado de jugadores agrupado alfabéticamente por equipo.
- No hagas cambios grandes ni reemplaces archivos completos si se puede resolver con un cambio localizado.
- No inventes estados de pruebas o despliegue. No guardes secretos ni credenciales en el repositorio.
- Primero dime qué estado actual verificaste, qué está confirmado, qué falta comprobar y cuál sería el cambio mínimo. Después trabaja solo sobre lo que te autorice.

Mi objetivo ahora es continuar desde el estado real del repositorio, no desde una suposición ni solo desde un resumen.
