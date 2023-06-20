import app.mortgage_calculator as mc
from app.mortgage_calculator import PAYEMNT_FRE
import pytest
from itertools import product

AMMORTIZATION_VALUES = [25, 20, 30]
FREQ_VALUES = [f for f in PAYEMNT_FRE]
INPUT_VALUES = list(product(AMMORTIZATION_VALUES, FREQ_VALUES))

params = {
                    'price': 830_000,
                    'down_payment': 130_000,
                    'utility': 650,
                    'utility_increment': 1.01,
                    'apr': 0.07,
                    'ammortization': 25,
                    'rent': 2800,
                    'rent_increment': 1.025,
                    'year_freq': PAYEMNT_FRE.MONTHLY,
                }


@pytest.mark.parametrize("ammortization_length,period_count", INPUT_VALUES)
def test_lenght(ammortization_length, period_count):
    params['year_freq'] = period_count
    params['ammortization'] = ammortization_length
    df = mc.mortgage_balance_calculator(params)
    assert len(df) == period_count.value * ammortization_length
