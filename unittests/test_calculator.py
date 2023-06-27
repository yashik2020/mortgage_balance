import app.mortgage_calculator as mc
from app.mortgage_calculator import PaymentFre
import pytest
from itertools import product

AMMORTIZATION_VALUES = [25, 20, 30]
FREQ_VALUES = [f for f in PaymentFre]
INPUT_VALUES = list(product(AMMORTIZATION_VALUES, FREQ_VALUES))

params = mc.default_params.copy()


def test_total_interest():
    params['price'] = 700_000
    params['down_payment'] = 100_000
    params['apr'] = 0.055
    df = mc.mortgage_balance_calculator(params)
    assert abs(df.iloc[-1]['Interest Paid Cumulative'] - 500_000) < 10_000


@pytest.mark.parametrize("ammortization_length,period_count", INPUT_VALUES)
def test_lenght(ammortization_length, period_count):
    params['year_freq'] = period_count
    params['ammortization'] = ammortization_length
    df = mc.mortgage_balance_calculator(params)
    assert len(df) == period_count.value * ammortization_length

