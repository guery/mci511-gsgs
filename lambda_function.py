"""MCI-511 Reto 10: acceso controlado a S3, URLs prefirmadas y Secrets Manager.
Runtime: Python 3.12. Handler: lambda_function.lambda_handler.
No imprime secretos, contenido de objetos ni URLs firmadas.
"""
import base64
import json
import logging
import os
from urllib.parse import unquote

import boto3
from botocore.exceptions import ClientError, BotoCoreError

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
REGION = os.environ.get('AWS_REGION', 'us-east-1')
BUCKET = os.environ.get('BUCKET_NAME', 'mci511-seguridad-guery')
SECRET_ID = os.environ.get('SECRET_ID', 'mci511/seguridad/credencial-demo')
ALLOWED_PREFIX = 'doc_permitidos/'
DENIED_PREFIX = 'doc_restringidos/'
S3 = boto3.client('s3', region_name=REGION)
SECRETS = boto3.client('secretsmanager', region_name=REGION)


def response(code, data):
    return {'statusCode': code, 'headers': {'Content-Type': 'application/json; charset=utf-8'},
            'body': json.dumps(data, ensure_ascii=False)}


def parse_event(event):
    if not isinstance(event, dict):
        raise ValueError('Evento inválido')
    if isinstance(event.get('body'), str):
        data = json.loads(event['body'] or '{}')
    elif isinstance(event.get('body'), dict):
        data = event['body']
    else:
        data = event
    if not isinstance(data, dict):
        raise ValueError('El cuerpo debe ser un objeto JSON')
    return data


def valid_key(key):
    if not isinstance(key, str) or not key.startswith(ALLOWED_PREFIX):
        return False
    # Evitar ambigüedades en nombres de objeto y rutas de prueba
    suffix = key[len(ALLOWED_PREFIX):]
    return bool(suffix) and not any(x in suffix for x in ('..', '\\', '//')) and not suffix.startswith('/')


def lambda_handler(event, context):
    request_id = getattr(context, 'aws_request_id', 'prueba-local')
    action = 'desconocida'
    try:
        data = parse_event(event)
        action = data.get('accion', '')
        if action == 'listar':
            result = S3.list_objects_v2(Bucket=BUCKET, Prefix=ALLOWED_PREFIX, MaxKeys=100)
            keys = [obj['Key'] for obj in result.get('Contents', []) if obj['Key'] != ALLOWED_PREFIX]
            payload = {'archivos': keys, 'truncado': result.get('IsTruncated', False)}
        elif action in ('leer', 'generar_url'):
            key = data.get('archivo', '')
            if not valid_key(key):
                LOGGER.warning('resultado=DENEGADO accion=%s request_id=%s', action, request_id)
                return response(403, {'resultado': 'DENEGADO', 'motivo': 'Objeto fuera del prefijo autorizado'})
            if action == 'leer':
                obj = S3.get_object(Bucket=BUCKET, Key=key)
                raw = obj['Body'].read(65537)
                if len(raw) > 65536:
                    return response(413, {'error': 'El archivo supera el límite de lectura de prueba (64 KiB)'})
                try:
                    content = raw.decode('utf-8')
                except UnicodeDecodeError:
                    return response(415, {'error': 'Solo se admiten archivos UTF-8 en esta prueba'})
                payload = {'archivo': key, 'contenido': content}
            else:
                ttl = data.get('duracion_segundos', 60)
                if type(ttl) is not int or not 1 <= ttl <= 300:
                    return response(400, {'error': 'duracion_segundos debe estar entre 1 y 300'})
                # Presign no comprueba necesariamente GetObject/KMS en este momento;
                # la descarga efectiva debe probarse por separado.
                url = S3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': key}, ExpiresIn=ttl)
                payload = {'archivo': key, 'url': url, 'duracion_segundos': ttl}
        elif action == 'consultar_secreto':
            # Solo se revela si se pudo recuperar; nunca se devuelve el valor.
            secret = SECRETS.get_secret_value(SecretId=SECRET_ID)
            payload = {'secreto': SECRET_ID, 'recuperado': 'SecretString' in secret or 'SecretBinary' in secret,
                       'version': secret.get('VersionId')}
        else:
            return response(400, {'error': 'Acción no válida', 'acciones': ['listar', 'leer', 'generar_url', 'consultar_secreto']})
        LOGGER.info('resultado=PERMITIDO accion=%s request_id=%s', action, request_id)
        return response(200, {'resultado': 'PERMITIDO', **payload})
    except (ValueError, json.JSONDecodeError):
        return response(400, {'error': 'Solicitud JSON inválida'})
    except ClientError as exc:
        error = exc.response.get('Error', {}).get('Code', 'AWS_ERROR')
        LOGGER.warning('resultado=ERROR_AWS accion=%s codigo=%s request_id=%s', action, error, request_id)
        status = 403 if error in ('AccessDenied', 'AccessDeniedException', 'KMS.AccessDeniedException') else 404 if error in ('NoSuchKey', 'ResourceNotFoundException') else 502
        return response(status, {'resultado': 'ERROR_AWS', 'codigo': error})
    except BotoCoreError:
        LOGGER.exception('Error de SDK AWS request_id=%s', request_id)
        return response(502, {'error': 'Error de comunicación con AWS'})
