"""Funciones auxiliares generales"""
import unicodedata
import re


def strip_accents(text: str) -> str:
    """
    Elimina acentos y diacríticos de un texto
    
    Args:
        text: Texto con posibles acentos
        
    Returns:
        Texto sin acentos
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def format_phone_number(phone: str) -> str:
    """
    Formatea un número de teléfono eliminando espacios y caracteres especiales
    
    Args:
        phone: Número de teléfono sin formato
        
    Returns:
        Número de teléfono limpio (solo dígitos)
    """
    return re.sub(r'\D', '', phone)


def validate_dni(dni: str) -> bool:
    """
    Valida que un DNI tenga 8 dígitos
    
    Args:
        dni: DNI a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    return bool(re.match(r'^\d{8}$', dni))


def validate_phone(phone: str) -> bool:
    """
    Valida que un teléfono tenga 10 dígitos
    
    Args:
        phone: Teléfono a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    return bool(re.match(r'^\d{10}$', phone))
