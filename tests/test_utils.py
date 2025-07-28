import datetime

import pandas as pd

from core.Utils import converter_para_hora


# --- Início dos Testes ---
# ===============================CONVERSÃO DE HORA===============================
def test_converter_hora_com_string_valida():
    """Testa se a função converte corretamente uma string de hora."""
    input_str = "14:30:05"
    expected_output = datetime.time(14, 30, 5)
    assert converter_para_hora(input_str) == expected_output


def test_converter_hora_com_timedelta_valido():
    """Testa se a função converte corretamente um objeto timedelta do pandas."""
    # O Pandas representa durações como Timedelta
    input_timedelta = pd.to_timedelta("10:20:30")
    expected_output = datetime.time(10, 20, 30)
    assert converter_para_hora(input_timedelta) == expected_output


def test_converter_hora_com_valor_nulo_pandas():
    """Testa se a função retorna None para um valor nulo do Pandas (NaT)."""
    input_null = pd.NaT
    assert converter_para_hora(input_null) is None


def test_converter_hora_com_valor_none_python():
    """Testa se a função retorna None para um valor None do Python."""
    input_none = None
    assert converter_para_hora(input_none) is None


def test_converter_hora_com_string_invalida():
    """Testa se a função retorna None para uma string mal formatada."""
    input_invalid_str = "hora_invalida"
    assert converter_para_hora(input_invalid_str) is None


def test_converter_hora_com_data_completa():
    """Testa se a função extrai a hora corretamente de um timestamp completo."""
    input_datetime_str = "2025-01-01 09:15:00"
    expected_output = datetime.time(9, 15, 0)
    assert converter_para_hora(input_datetime_str) == expected_output


def test_converter_hora_com_inteiro():
    """Testa se a função retorna None para um tipo de dado inesperado como um inteiro."""
    input_int = 12345
    assert converter_para_hora(input_int) is None


# ===============================================================================
