import app.mortgage_calculator as mc

AMMORTIZATION_25= 25

def test_lenght_monthly():
    df = mc.mortgage_balance_calculator(price= 830_000
                                        ,down_payment= 130_000
                                        ,utility= 650
                                        ,utility_increment = 1.01
                                        ,apr= 0.07
                                        ,ammortization= AMMORTIZATION_25
                                        ,rent= 2800
                                        ,rent_increment = 1.025
                                        ,year_freq = mc.PAYEMNT_FRE.MONTHLY)
    assert len(df) == mc.PAYEMNT_FRE.MONTHLY.value * AMMORTIZATION_25


def test_lenght_biweekly():
    df = mc.mortgage_balance_calculator(price= 830_000
                                        ,down_payment= 130_000
                                        ,utility= 650
                                        ,utility_increment = 1.01
                                        ,apr= 0.07
                                        ,ammortization= AMMORTIZATION_25
                                        ,rent= 2800
                                        ,rent_increment = 1.025
                                        ,year_freq = mc.PAYEMNT_FRE.BIWEEKLY)
    assert len(df) == mc.PAYEMNT_FRE.BIWEEKLY.value * AMMORTIZATION_25


def test_lenght_weekly():
    df = mc.mortgage_balance_calculator(price= 830_000
                                        ,down_payment= 130_000
                                        ,utility= 650
                                        ,utility_increment = 1.01
                                        ,apr= 0.07
                                        ,ammortization= AMMORTIZATION_25
                                        ,rent= 2800
                                        ,rent_increment = 1.025
                                        ,year_freq = mc.PAYEMNT_FRE.WEEKLY)
    assert len(df) == mc.PAYEMNT_FRE.WEEKLY.value * AMMORTIZATION_25

