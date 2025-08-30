"""
Utilitários para formatação e conversão de datas.

Este módulo centraliza todas as operações com datas na aplicação,
garantindo consistência entre exibição (DD/MM/YYYY) e envio para API (YYYY-MM-DD).
"""

from datetime import datetime, date
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

# Formatos padrão
DISPLAY_FORMAT = "%d/%m/%Y"  # DD/MM/YYYY para exibição
API_FORMAT = "%Y-%m-%d"      # YYYY-MM-DD para API
DATETIME_DISPLAY_FORMAT = "%d/%m/%Y %H:%M"  # DD/MM/YYYY HH:MM para exibição com hora
DATETIME_API_FORMAT = "%Y-%m-%d %H:%M:%S"   # YYYY-MM-DD HH:MM:SS para API com hora


def format_date_for_display(date_value: Union[str, date, datetime, None]) -> str:
    """
    Formata uma data para exibição (DD/MM/YYYY).
    
    Parameters
    ----------
    date_value : Union[str, date, datetime, None]
        Data a ser formatada
        
    Returns
    -------
    str
        Data formatada para exibição ou string vazia se inválida
    """
    if not date_value:
        return ""
        
    try:
        if isinstance(date_value, str):
            # Tenta diferentes formatos de string
            for fmt in [API_FORMAT, DISPLAY_FORMAT, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    return parsed_date.strftime(DISPLAY_FORMAT)
                except ValueError:
                    continue
            
            # Se não conseguiu parsear, retorna a string original
            logger.warning(f"Não foi possível parsear a data: {date_value}")
            return str(date_value)
            
        elif isinstance(date_value, datetime):
            return date_value.strftime(DISPLAY_FORMAT)
            
        elif isinstance(date_value, date):
            return date_value.strftime(DISPLAY_FORMAT)
            
        else:
            return str(date_value)
            
    except Exception as e:
        logger.error(f"Erro ao formatar data para exibição: {e}")
        return str(date_value) if date_value else ""


def format_date_for_api(date_value: Union[str, date, datetime, None]) -> str:
    """
    Formata uma data para envio à API (YYYY-MM-DD).
    
    Parameters
    ----------
    date_value : Union[str, date, datetime, None]
        Data a ser formatada
        
    Returns
    -------
    str
        Data formatada para API ou string vazia se inválida
    """
    if not date_value:
        return ""
        
    try:
        if isinstance(date_value, str):
            # Tenta diferentes formatos de string
            for fmt in [DISPLAY_FORMAT, API_FORMAT, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    return parsed_date.strftime(API_FORMAT)
                except ValueError:
                    continue
            
            # Se não conseguiu parsear, tenta interpretar como já está no formato da API
            logger.warning(f"Não foi possível parsear a data: {date_value}")
            return str(date_value)
            
        elif isinstance(date_value, datetime):
            return date_value.strftime(API_FORMAT)
            
        elif isinstance(date_value, date):
            return date_value.strftime(API_FORMAT)
            
        else:
            return str(date_value)
            
    except Exception as e:
        logger.error(f"Erro ao formatar data para API: {e}")
        return str(date_value) if date_value else ""


def format_datetime_for_display(datetime_value: Union[str, datetime, None]) -> str:
    """
    Formata uma data/hora para exibição (DD/MM/YYYY HH:MM).
    
    Parameters
    ----------
    datetime_value : Union[str, datetime, None]
        Data/hora a ser formatada
        
    Returns
    -------
    str
        Data/hora formatada para exibição ou string vazia se inválida
    """
    if not datetime_value:
        return ""
        
    try:
        if isinstance(datetime_value, str):
            # Tenta diferentes formatos de string
            for fmt in [DATETIME_API_FORMAT, DATETIME_DISPLAY_FORMAT, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    parsed_datetime = datetime.strptime(datetime_value, fmt)
                    return parsed_datetime.strftime(DATETIME_DISPLAY_FORMAT)
                except ValueError:
                    continue
            
            # Se não conseguiu parsear, retorna a string original
            logger.warning(f"Não foi possível parsear a data/hora: {datetime_value}")
            return str(datetime_value)
            
        elif isinstance(datetime_value, datetime):
            return datetime_value.strftime(DATETIME_DISPLAY_FORMAT)
            
        else:
            return str(datetime_value)
            
    except Exception as e:
        logger.error(f"Erro ao formatar data/hora para exibição: {e}")
        return str(datetime_value) if datetime_value else ""


def format_datetime_for_api(datetime_value: Union[str, datetime, None]) -> str:
    """
    Formata uma data/hora para envio à API (YYYY-MM-DD HH:MM:SS).
    
    Parameters
    ----------
    datetime_value : Union[str, datetime, None]
        Data/hora a ser formatada
        
    Returns
    -------
    str
        Data/hora formatada para API ou string vazia se inválida
    """
    if not datetime_value:
        return ""
        
    try:
        if isinstance(datetime_value, str):
            # Tenta diferentes formatos de string
            for fmt in [DATETIME_DISPLAY_FORMAT, DATETIME_API_FORMAT, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    parsed_datetime = datetime.strptime(datetime_value, fmt)
                    return parsed_datetime.strftime(DATETIME_API_FORMAT)
                except ValueError:
                    continue
            
            # Se não conseguiu parsear, retorna a string original
            logger.warning(f"Não foi possível parsear a data/hora: {datetime_value}")
            return str(datetime_value)
            
        elif isinstance(datetime_value, datetime):
            return datetime_value.strftime(DATETIME_API_FORMAT)
            
        else:
            return str(datetime_value)
            
    except Exception as e:
        logger.error(f"Erro ao formatar data/hora para API: {e}")
        return str(datetime_value) if datetime_value else ""


def parse_date_from_string(date_string: str) -> Optional[date]:
    """
    Converte string de data para objeto date.
    
    Parameters
    ----------
    date_string : str
        String da data a ser convertida
        
    Returns
    -------
    Optional[date]
        Objeto date ou None se não foi possível converter
    """
    if not date_string:
        return None
        
    try:
        # Tenta diferentes formatos
        for fmt in [DISPLAY_FORMAT, API_FORMAT, "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Não foi possível converter string para date: {date_string}")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao converter string para date: {e}")
        return None


def get_today_for_display() -> str:
    """
    Retorna a data de hoje formatada para exibição.
    
    Returns
    -------
    str
        Data de hoje no formato DD/MM/YYYY
    """
    return datetime.now().strftime(DISPLAY_FORMAT)


def get_today_for_api() -> str:
    """
    Retorna a data de hoje formatada para API.
    
    Returns
    -------
    str
        Data de hoje no formato YYYY-MM-DD
    """
    return datetime.now().strftime(API_FORMAT)


def is_valid_date_string(date_string: str) -> bool:
    """
    Verifica se uma string representa uma data válida.
    
    Parameters
    ----------
    date_string : str
        String a ser validada
        
    Returns
    -------
    bool
        True se é uma data válida
    """
    return parse_date_from_string(date_string) is not None


def format_currency_br(value: Union[int, float, str, None]) -> str:
    """
    Formata um valor monetário para o padrão brasileiro (vírgula como separador decimal).
    
    Parameters
    ----------
    value : Union[int, float, str, None]
        Valor a ser formatado
        
    Returns
    -------
    str
        Valor formatado no padrão brasileiro (R$ 1.234,56)
    """
    if value is None:
        return "R$ 0,00"
    
    try:
        # Converte para float se necessário
        if isinstance(value, str):
            value = float(value)
        
        # Formata usando o padrão brasileiro: separa milhares com ponto e decimais com vírgula
        formatted = f"{float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"R$ {formatted}"
        
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao formatar valor monetário: {value}, erro: {e}")
        return "R$ 0,00"