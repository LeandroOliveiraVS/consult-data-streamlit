import pandas as pd
import datetime


def converter_para_hora(valor):
    """Converte um valor (string ou timedelta) para um objeto time."""
    if pd.isnull(valor):
        return None
    try:
        # Converte para string e pega a última parte (ex: "14:30:00")
        # Funciona tanto para "14:30:00" como para "0 days 14:30:00"
        hora_str = str(valor).split()[-1]
        # Converte a string da hora para um objeto time
        return datetime.datetime.strptime(hora_str, "%H:%M:%S").time()
    except (ValueError, TypeError):
        # Retorna None se a conversão falhar
        return None
