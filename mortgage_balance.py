import pandas as pd
from enum import Enum
from os import path


class PAYEMNT_FRE(Enum):
    MONTHLY = 12
    WEEKLY = 54
    BIWEEKLY = 27


PRICE= 830_000
DOWN_PAYMENT= 130_000
UTILITY= 650 * 12
UTILITY_INCREMENT = 1.01
APR= 0.07
AMMORTIZATION= 25
RENT= 2800 * 12
RENT_INCREMENT = 1.025

year_freq = PAYEMNT_FRE.BIWEEKLY

rate = APR / year_freq.value
periods = AMMORTIZATION * year_freq.value
principal = PRICE - DOWN_PAYMENT
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
           round((APR / year_freq.value) * principal ,2),
           round(period_payment -  ((APR / year_freq.value) * principal), 2),
           round(UTILITY / year_freq.value, 2),
           round(RENT / year_freq.value, 2),
           ]

for i in range(2, AMMORTIZATION * year_freq.value + 1):
    last_year = df[df.Period == i - 1]
    starting_principal = last_year.iloc[0]['Starting Principal'] - last_year.iloc[0]['Principal Paid']
    temp = [i, 
            starting_principal, 
            period_payment, 
            (APR / year_freq.value) * starting_principal, 
            period_payment -  ((APR / year_freq.value) * starting_principal),
            (UTILITY * (UTILITY_INCREMENT ** ((i-1)//year_freq.value))) / year_freq.value,
            (RENT * (RENT_INCREMENT ** ((i-1)//year_freq.value))) / year_freq.value,
            ]
    temp = [round(x, 2) for x in temp]
    df.loc[len(df)] = temp

df['Costs Paid Cumulative'] = df['Interest Paid'] + df['Utility']
df['Costs Paid Cumulative'] = df['Costs Paid Cumulative'].cumsum()
df['Rent Save Cumulative'] = df['Rent'].cumsum()

df['Costs Paid Cumulative'] = df['Costs Paid Cumulative'].apply(lambda x: round(x, 2))
df['Rent Save Cumulative'] = df['Rent Save Cumulative'].apply(lambda x: round(x, 2))

print(df.head())
print(df.tail())
# df.to_excel(path.join(path.dirname(__file__), 'ammortization.xlsx'), index=False)