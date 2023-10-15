from os import path
from enum import Enum
import pandas as pd


class PaymentFre(Enum):
    MONTHLY = 12
    WEEKLY = 52
    BIWEEKLY = 26


PROPERTY_TAX = 0.0066
LAND_TRANSFER = 20_000
CLOSING_FEE = 0.03
INVESTMENT_RATE = 0.04


default_params = {
                    'price': 830_000,
                    'down_payment': 130_000,
                    'utility': 650,
                    'utility_increment': 1.01,
                    'apr': 0.07,
                    'ammortization': 25,
                    'rent': 2800,
                    'rent_increment': 1.025,
                    'year_freq': PaymentFre.MONTHLY,
                    'appreciation': 0.04,
                }


def mortgage_balance_calculator(parameters=default_params, **kwargs):
    try:
        price= parameters['price']
        down_payment= parameters['down_payment']
        utility= parameters['utility']
        utility_increment = parameters['utility_increment']
        apr= parameters['apr']
        ammortization= parameters['ammortization']
        rent= parameters['rent']
        rent_increment = parameters['rent_increment']
        year_freq = parameters['year_freq']
        appreciation = parameters['appreciation']
    except KeyError as exc:
        #TODO: Handle the input error
        raise KeyError('Parameters are not set correctly') from exc
    
    rent = rent * 12
    utility = utility * 12
    rate = apr / year_freq.value
    periods = ammortization * year_freq.value
    principal = price - down_payment
    period_payment = round(principal * (rate*(1 + rate)**periods)/((1+rate)**periods-1), 2)


    df = pd.DataFrame(columns=[
        'Period',
        'Starting Principal',
        'Mortgage Payment',
        'Interest Paid',
        'Principal Paid',
        'Utility',
        'Property Tax',
        'Investment Loss',
        'Rent',
        'Property Appreciation',
    ])

    df.loc[len(df)] = [1, 
                       principal,
                       period_payment,
                       (apr / year_freq.value) * principal,
                       period_payment -  ((apr / year_freq.value) * principal),
                       utility / year_freq.value,
                       (price * PROPERTY_TAX) / year_freq.value,
                       (down_payment * INVESTMENT_RATE) / year_freq.value,
                       rent / year_freq.value,
                       (price * appreciation) / year_freq.value,
                       ]

    for i in range(2, ammortization * year_freq.value + 1):
        last_year = df[df.Period == i - 1]
        starting_principal = last_year.iloc[0]['Starting Principal'] - last_year.iloc[0]['Principal Paid']
        temp = [i,
                starting_principal,
                period_payment,
                (apr / year_freq.value) * starting_principal,
                period_payment -  ((apr / year_freq.value) * starting_principal),
                (utility * (utility_increment ** ((i-1)//year_freq.value))) / year_freq.value,
                (price * PROPERTY_TAX) / year_freq.value,
                ((down_payment * ((1+INVESTMENT_RATE) ** ((i-1)//year_freq.value)))*INVESTMENT_RATE) / year_freq.value,
                (rent * (rent_increment ** ((i-1)//year_freq.value))) / year_freq.value,
                ((price * appreciation) * ((1+appreciation) ** (i//year_freq.value))) / year_freq.value,
                ]
        temp = [round(x, 2) for x in temp]
        df.loc[len(df)] = temp

    df['Costs'] = df['Interest Paid'] + df['Utility'] + df['Property Tax'] + df['Investment Loss']
    df['Interest Paid Cumulative'] = df['Interest Paid'].cumsum()
    df['Utility Paid Cumulative'] = df['Utility'].cumsum()
    df['Costs Cumulative'] = df['Costs'].cumsum()
    # df['Costs Cumulative'] = df['Costs Cumulative'] + (CLOSING_FEE * price)
    df['Rent Save Cumulative'] = df['Rent'].cumsum()
    df['Interest Ratio'] = (df['Interest Paid']/df['Mortgage Payment']) * 100
    df['Profit and Liquidity'] = df['Rent'] + df['Principal Paid']
    df['Profit and Liquidity'] = df['Profit and Liquidity'].cumsum()


    df = df.apply(lambda x: round(x, 2))

    if kwargs.get('write_to_file') is True:
        df.to_excel(path.join(path.dirname(__file__), 'ammortization.xlsx'), index=False)

    return df

# df = mortgage_balance_calculator()

# print(df.head())