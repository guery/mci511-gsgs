MCI-511 | Reto 10 | Lambda

Nombre: mci511-auditoria-lambda
Runtime: Python 3.14
Handler: lambda_function.lambda_handler
Architecture: x86_64
Execution role: LabRole (si permite crear la función y ejecutar acciones requeridas)
Timeout: 15 segundos
Memory: 128 MB
Environment variables:
  BUCKET_NAME=mci511-seguridad-guery
  SECRET_ID=mci511/seguridad/credencial-demo

PRUEBAS EN LA CONSOLA LAMBDA (Test -> JSON):
1. Listar:
{"accion":"listar"}
2. Leer autorizado:
{"accion":"leer","archivo":"doc_permitidos/01_presentacion_proyecto.txt"}
3. Denegación en la aplicación:
{"accion":"leer","archivo":"doc_restringidos/01_informe_interno.txt"}
4. Generar URL (no publicar URL ni compartir captura con su valor):
{"accion":"generar_url","archivo":"doc_permitidos/01_presentacion_proyecto.txt","duracion_segundos":60}
5. Recuperar secreto (después de crearlo):
{"accion":"consultar_secreto"}

IMPORTANTE:
- Un 403 de la prueba 3 demuestra rechazo en el código, no denegación IAM.
- Para demostrar mínimo privilegio habrá que configurar y verificar IAM/S3 en una etapa posterior.
- Una URL prefirmada puede generarse sin comprobar permisos de descarga; verificar su uso real.
- La función no debe exponerse públicamente sin autenticación/autorización en API Gateway.
- El valor de la URL firmada y el secreto no deben figurar en el informe.
- La descarga con SSE-KMS puede exigir kms:Decrypt en el rol de ejecución.
