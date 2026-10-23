from pathlib import Path

BASE = Path(__file__).resolve().parent
DOCUMENTOS = {
    'doc_permitidos': {
        '01_presentacion_proyecto.txt': 'Proyecto MCI-511 - Reto 10\nDocumento de prueba: presentación general.\nClasificación: uso de laboratorio.\nContenido: demostración de lectura autorizada desde Amazon S3.\n',
        '02_manual_consulta.txt': 'Proyecto MCI-511 - Reto 10\nManual de consulta de prueba.\nClasificación: uso de laboratorio.\nContenido: este archivo puede ser descargado mediante una URL prefirmada válida.\n',
        '03_reporte_publicable.txt': 'Proyecto MCI-511 - Reto 10\nReporte ficticio para pruebas.\nClasificación: uso de laboratorio.\nContenido: no incluye información real, credenciales ni datos personales.\n',
        '04_control_integridad.txt': 'Proyecto MCI-511 - Reto 10\nArchivo de control de integridad.\nClasificación: uso de laboratorio.\nContenido: verificar lectura y comparación de hash SHA-256.\n',
    },
    'doc_restringidos': {
        '01_informe_interno.txt': 'Proyecto MCI-511 - Reto 10\nInforme interno ficticio.\nClasificación simulada: restringido.\nContenido: prueba de acceso denegado mediante política de S3.\n',
        '02_registro_auditoria.txt': 'Proyecto MCI-511 - Reto 10\nRegistro de auditoría ficticio.\nClasificación simulada: restringido.\nContenido: eventos inventados únicamente como datos de prueba; no representan resultados reales de AWS.\n',
        '03_configuracion_reservada.txt': 'Proyecto MCI-511 - Reto 10\nConfiguración reservada ficticia.\nClasificación simulada: restringido.\nContenido: no contiene claves, tokens ni contraseñas reales.\n',
        '04_datos_controlados.txt': 'Proyecto MCI-511 - Reto 10\nDatos controlados ficticios.\nClasificación simulada: restringido.\nContenido: prueba de rechazo de descarga y de generación de URL no autorizada.\n',
    },
}

if __name__ == '__main__':
    for carpeta, archivos in DOCUMENTOS.items():
        destino = BASE / carpeta
        destino.mkdir(parents=True, exist_ok=True)
        for nombre, contenido in archivos.items():
            ruta = destino / nombre
            ruta.write_text(contenido, encoding='utf-8')
            print(f'Generado: {ruta.relative_to(BASE)}')
