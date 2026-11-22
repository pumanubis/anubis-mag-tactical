# REGLAS DE TRABAJO Y PROMPT PARA OTRO CHAT

## Preferencia de autonomía del usuario
La preferencia acordada para los tres proyectos ANUBIS MAG es **máxima autonomía**: ejecutar cambios, pruebas, correcciones y publicación sin pedir aprobación por cada paso, cuando las herramientas lo permitan. La publicación debe ser automática después de superar las validaciones.

La política completa y sus excepciones están en `docs/continuidad/05_AUTONOMIA_Y_PUBLICACION.md`. Esta preferencia no elimina límites de permisos, protecciones de rama ni solicitudes de autorización de la plataforma.

## Reglas que debe seguir el asistente
1. Responder en español, con instrucciones claras y prácticas.
2. Antes de modificar código, abrir y revisar el archivo real de la rama actual.
3. No inventar funciones, pruebas, resultados, URLs, commits ni estados de despliegue.
4. Mantener separados TACTICAL, RESPAWN y MISSIONS.
5. No reemplazar el archivo completo ni reescribir módulos grandes cuando basta un cambio localizado.
6. No quitar ni alterar una función que ya trabaja; preservar compatibilidad y comportamiento existente.
7. En cambios de base de datos, revisar esquema, funciones, políticas y migraciones existentes antes de ejecutar SQL.
8. Nunca pedir ni escribir contraseñas, tokens, claves secretas o códigos de autenticación en archivos de documentación o en el repositorio.
9. Distinguir claramente entre: confirmado por el código, confirmado en producción, decisión acordada y tarea pendiente.
10. Después de cada cambio, validar sintaxis, revisar el diff y comprobar el despliegue si aplica.
11. Aplicar máxima autonomía a cambios rutinarios y reversibles: implementar, probar, corregir, hacer commit y publicar automáticamente si las validaciones pasan y los permisos lo permiten.
12. Detenerse y pedir confirmación únicamente para operaciones de alto riesgo o irreversibles descritas en la política de autonomía, o cuando la herramienta/plataforma exija una autorización.
13. Si no se puede comprobar algo, decirlo y pedir el dato mínimo necesario en lugar de adivinar.

## Prompt listo para copiar y pegar en un nuevo chat

Estoy continuando uno de los proyectos ANUBIS MAG y no quiero empezar desde cero. Trabaja en español y sigue las reglas de continuidad del repositorio correspondiente.

- Mi preferencia es máxima autonomía: ejecuta los cambios solicitados, pruebas, correcciones y publicación sin pedir aprobación por cada paso cuando las herramientas lo permitan.
- Publica automáticamente después de que pasen las validaciones.
- Revisa el código vigente, el último commit y el estado real del despliegue antes de actuar.
- Haz cambios pequeños, preserva las funciones existentes y verifica el resultado real.
- Detente solo ante operaciones de alto riesgo/irreversibles, fallos críticos de validación o una autorización que la plataforma exija.
- No inventes resultados y no guardes secretos en el repositorio.
- Consulta `docs/continuidad/05_AUTONOMIA_Y_PUBLICACION.md` para conocer el protocolo completo.
- Mantén ANUBIS MAG TACTICAL, RESPAWN ANUBIS MAG y ANUBIS MAG MISSIONS como proyectos separados.

Después de cada tarea, informa brevemente el cambio, las validaciones, el commit y el estado de publicación; diferencia claramente lo verificado de lo que no pudo comprobarse.
