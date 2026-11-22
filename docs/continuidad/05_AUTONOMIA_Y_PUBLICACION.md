# POLÍTICA DE AUTONOMÍA Y PUBLICACIÓN — ANUBIS MAG

**Preferencia acordada por el usuario (22 de noviembre de 2026): máxima autonomía.** Aplicar a TACTICAL, RESPAWN ANUBIS MAG y ANUBIS MAG MISSIONS.

## Modo de trabajo predeterminado
- Ejecutar directamente, sin pedir aprobación paso a paso, los cambios rutinarios, acotados y reversibles que estén dentro de la solicitud del usuario.
- Revisar el código y configuración vigentes antes de editar; hacer el cambio mínimo y preservar las funciones existentes.
- Ejecutar las pruebas disponibles, corregir fallos detectados, revisar el diff y repetir validaciones.
- Crear commits y publicar automáticamente después de que las validaciones pasen, cuando los permisos, el flujo de despliegue y las herramientas disponibles lo permitan.
- Verificar el resultado real del despliegue y comunicar de forma breve qué cambió, qué pruebas pasaron, el commit y el estado de publicación. Nunca afirmar que una prueba o publicación ocurrió si no se comprobó.
- Si una validación falla, no promover ni publicar esa versión; intentar corregirla dentro del alcance, volver a probar y, si sigue fallando o falta información esencial, explicar el bloqueo y pedir solo lo estrictamente necesario.
- Mantener separados TACTICAL, RESPAWN y MISSIONS; no trasladar cambios entre repositorios por suposición.
- No reemplazar archivos grandes ni reescribir módulos completos si basta un cambio localizado. Conservar las funciones ya operativas.

## Casos que sí requieren detenerse o pedir confirmación
La preferencia de máxima autonomía no autoriza acciones con riesgo importante o irreversible. Detenerse antes de:
- borrar datos de producción, tablas, archivos o historiales sin recuperación verificada;
- ejecutar migraciones que puedan perder o transformar datos de forma irreversible;
- cambiar autenticación, permisos, políticas RLS, secretos, credenciales o controles de seguridad de manera sustancial;
- contratar servicios, generar gastos o aumentar límites de pago;
- sobrescribir trabajo ajeno/no revisado, forzar cambios destructivos de Git o eliminar respaldos;
- ampliar el alcance a otros proyectos o funciones no solicitadas;
- publicar cuando las pruebas críticas fallen, haya errores de seguridad o no pueda determinarse el impacto.
Antes de una operación de alto riesgo, describir el riesgo y la alternativa segura. No pedir aprobación para cada paso rutinario.

## Seguridad y credenciales
- Nunca guardar contraseñas, tokens, claves privadas, claves secretas de Supabase ni códigos de autenticación en el repositorio o documentos de continuidad.
- Usar GitHub Actions Secrets/Variables, secretos de entorno o mecanismos oficiales equivalentes.
- No mostrar secretos en logs, commits, capturas ni respuestas.
- Preferir mínimo privilegio, respaldos y cambios reversibles.

## Condiciones técnicas y límites reales
Esta política expresa la preferencia de trabajo, pero no puede anular los permisos de GitHub/Supabase, las protecciones de rama, los secretos requeridos, las aprobaciones de despliegue ni los avisos de seguridad de ChatGPT. Si una herramienta solicita autorización o la conexión carece de permisos, explicar exactamente qué ajuste o intervención puntual falta; no fingir que se puede omitir ese control.

## Lista de cierre para cada cambio
1. Confirmar repositorio, rama y estado actual.
2. Ejecutar pruebas/lint/build disponibles y revisar el diff.
3. Corregir fallos y volver a validar.
4. Si las comprobaciones requeridas pasan, hacer commit y publicar automáticamente cuando esté habilitado.
5. Verificar el despliegue real y registrar commit, pruebas, resultado y cualquier limitación.
