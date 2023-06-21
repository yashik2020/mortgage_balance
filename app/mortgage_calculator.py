from os import path
from enum import Enum
import pandas as pd


class PaymentFre(Enum):
    MONTHLY = 12
    WEEKLY = 54
    BIWEEKLY = 27

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
        'Rent'
    ])

    df.loc[len(df)] = [1, principal, 
            period_payment, 
            round((apr / year_freq.value) * principal ,2),
            round(period_payment -  ((apr / year_freq.value) * principal), 2),
            round(utility / year_freq.value, 2),
            round(rent / year_freq.value, 2),
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
                (rent * (rent_increment ** ((i-1)//year_freq.value))) / year_freq.value,
                ]
        temp = [round(x, 2) for x in temp]
        df.loc[len(df)] = temp

    df['Costs Paid Cumulative'] = df['Interest Paid'] + df['Utility']
    df['Interest Paid Cumulative'] = df['Interest Paid'].cumsum()
    df['Utility Paid Cumulative'] = df['Utility'].cumsum()
    df['Costs Paid Cumulative'] = df['Costs Paid Cumulative'].cumsum()
    df['Rent Save Cumulative'] = df['Rent'].cumsum()

    df['Costs Paid Cumulative'] = df['Costs Paid Cumulative'].apply(lambda x: round(x, 2))
    df['Rent Save Cumulative'] = df['Rent Save Cumulative'].apply(lambda x: round(x, 2))
    df['Interest Paid Cumulative'] = df['Interest Paid Cumulative'].apply(lambda x: round(x, 2))
    df['Utility Paid Cumulative'] = df['Utility Paid Cumulative'].apply(lambda x: round(x, 2))

    df['Interest Ratio'] = (df['Interest Paid']/df['Mortgage Payment']) * 100

    if kwargs.get('write_to_file') is True:
        df.to_excel(path.join(path.dirname(__file__), 'ammortization.xlsx'), index=False)

    return df
