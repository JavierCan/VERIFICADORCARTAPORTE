# utils.py

def parse_float(value: str) -> float:
    """
    Convierte una cadena a float. Retorna 0.0 en caso de error.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def format_and_compare_liters(facturada_str: str, transportada_str: str) -> tuple[str, str, str]:
    """
    Convierte las cantidades facturada y transportada a float, las formatea con 3 decimales y
    retorna ambas cadenas formateadas junto a una comparación ("Iguales" o "Diferentes").
    """
    facturada_val = parse_float(facturada_str)
    transportada_val = parse_float(transportada_str)
    facturada_fmt = f"{facturada_val:.3f}"
    transportada_fmt = f"{transportada_val:.3f}"
    comparacion = "Iguales" if abs(facturada_val - transportada_val) < 1e-9 else "Diferentes"
    return facturada_fmt, transportada_fmt, comparacion

def map_clave_to_combustible(clave_prod_serv: str) -> str:
    """
    Mapea la clave SAT al tipo de combustible correspondiente.
    """
    mapping = {
        '15101514': 'magna',
        '15101515': 'premium',
        '15101505': 'diesel'
    }
    return mapping.get(clave_prod_serv)
