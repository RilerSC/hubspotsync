# utils/security.py
"""
Módulo de seguridad para validación, sanitización y protección de datos sensibles
"""
import re
from typing import Any, Optional, List


class SecurityError(Exception):
    """Excepción personalizada para errores de seguridad"""
    pass


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitiza un identificador SQL (nombre de tabla o columna) para prevenir SQL Injection.

    Solo permite caracteres alfanuméricos, guiones bajos y guiones.
    Los identificadores deben comenzar con una letra o guión bajo.

    Args:
        identifier: Nombre de tabla o columna a sanitizar

    Returns:
        Identificador sanitizado

    Raises:
        SecurityError: Si el identificador contiene caracteres no permitidos
    """
    if not identifier:
        raise SecurityError("El identificador SQL no puede estar vacío")

    # Validar formato: solo letras, números, guiones bajos y guiones
    # Debe comenzar con letra o guión bajo
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', identifier):
        raise SecurityError(
            f"Identificador SQL inválido: '{identifier}'. "
            "Solo se permiten letras, números, guiones bajos y guiones. "
            "Debe comenzar con letra o guión bajo."
        )

    # Limitar longitud para prevenir ataques de buffer overflow
    if len(identifier) > 128:
        raise SecurityError(f"Identificador SQL demasiado largo: {len(identifier)} caracteres (máximo 128)")

    return identifier


def sanitize_sql_identifiers(identifiers: List[str]) -> List[str]:
    """
    Sanitiza una lista de identificadores SQL.

    Args:
        identifiers: Lista de nombres de tablas o columnas

    Returns:
        Lista de identificadores sanitizados

    Raises:
        SecurityError: Si algún identificador es inválido
    """
    return [sanitize_sql_identifier(identifier) for identifier in identifiers]


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Enmascara datos sensibles mostrando solo los últimos caracteres visibles.

    Args:
        data: String con datos sensibles
        visible_chars: Número de caracteres visibles al final (default: 4)

    Returns:
        String enmascarado (ej: "****1234")
    """
    if not data:
        return "****"

    if len(data) <= visible_chars:
        return "*" * len(data)

    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def mask_connection_string(connection_string: str) -> str:
    """
    Enmascara credenciales en una cadena de conexión SQL Server.

    Args:
        connection_string: Cadena de conexión completa

    Returns:
        Cadena de conexión con credenciales enmascaradas
    """
    # Enmascarar PWD (password)
    connection_string = re.sub(
        r'PWD=([^;]+)',
        lambda m: f'PWD={mask_sensitive_data(m.group(1))}',
        connection_string,
        flags=re.IGNORECASE
    )

    # Enmascarar UID si contiene información sensible
    connection_string = re.sub(
        r'UID=([^;]+)',
        lambda m: f'UID={mask_sensitive_data(m.group(1), visible_chars=2)}',
        connection_string,
        flags=re.IGNORECASE
    )

    return connection_string


def validate_cedula(cedula: str) -> bool:
    """
    Valida el formato de un número de cédula costarricense.

    Formato esperado: 8-12 dígitos numéricos

    Args:
        cedula: Número de cédula a validar

    Returns:
        True si el formato es válido, False en caso contrario
    """
    if not cedula:
        return False

    # Remover espacios y guiones
    cedula_clean = re.sub(r'[\s-]', '', str(cedula))

    # Validar que sean solo dígitos y tenga longitud válida
    if not re.match(r'^\d{8,12}$', cedula_clean):
        return False

    return True


def sanitize_string(value: Any, max_length: int = 1000) -> Optional[str]:
    """
    Sanitiza un valor de string para prevenir inyección y corrupción de datos.

    Args:
        value: Valor a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        String sanitizado o None si el valor es inválido
    """
    if value is None:
        return None

    # Convertir a string
    str_value = str(value)

    # Remover caracteres de control (excepto tab, newline, carriage return)
    str_value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', str_value)

    # Limitar longitud
    if len(str_value) > max_length:
        str_value = str_value[:max_length]

    return str_value.strip() if str_value.strip() else None


def validate_email(email: str) -> bool:
    """
    Valida el formato de un email usando expresión regular básica.

    Args:
        email: Email a validar

    Returns:
        True si el formato es válido, False en caso contrario
    """
    if not email:
        return False

    # Expresión regular básica para validar email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def sanitize_table_name(table_name: str) -> str:
    """
    Sanitiza y valida un nombre de tabla SQL.

    Args:
        table_name: Nombre de tabla a sanitizar

    Returns:
        Nombre de tabla sanitizado

    Raises:
        SecurityError: Si el nombre de tabla es inválido
    """
    # Whitelist de nombres de tablas permitidos
    ALLOWED_TABLES = {
        'hb_deals', 'hb_tickets', 'hb_contacts', 'hb_owners',
        'hb_deals_pipeline', 'hb_tickets_pipeline'
    }

    sanitized = sanitize_sql_identifier(table_name)

    # Verificar que esté en la whitelist
    if sanitized not in ALLOWED_TABLES:
        raise SecurityError(
            f"Nombre de tabla no permitido: '{table_name}'. "
            f"Tablas permitidas: {', '.join(ALLOWED_TABLES)}"
        )

    return sanitized




