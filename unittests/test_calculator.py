import app.mortgage_calculator as mc

AMMORTIZATION= 25

params_default = {
                    'price': 830_000,
                    'down_payment': 130_000,
                    'utility': 650,
                    'utility_increment': 1.01,
                    'apr': 0.07,
                    'ammortization': 25,
                    'rent': 2800,
                    'rent_increment': 1.025,
                    'year_freq': mc.PAYEMNT_FRE.MONTHLY,
                }

params_weekly_25 = params_default.copy()
params_weekly_25['year_freq'] = mc.PAYEMNT_FRE.WEEKLY
params_biweekly_25 = params_default.copy()
params_biweekly_25['year_freq'] = mc.PAYEMNT_FRE.BIWEEKLY
params_monthly_25 = params_default.copy()
params_monthly_25['year_freq'] = mc.PAYEMNT_FRE.MONTHLY


def test_lenght_monthly():
    df = mc.mortgage_balance_calculator(params_monthly_25)
    assert len(df) == mc.PAYEMNT_FRE.MONTHLY.value * AMMORTIZATION


def test_lenght_biweekly():
    df = mc.mortgage_balance_calculator(params_biweekly_25)
    assert len(df) == mc.PAYEMNT_FRE.BIWEEKLY.value * AMMORTIZATION


def test_lenght_weekly():
    df = mc.mortgage_balance_calculator(params_weekly_25)
    assert len(df) == mc.PAYEMNT_FRE.WEEKLY.value * AMMORTIZATION

