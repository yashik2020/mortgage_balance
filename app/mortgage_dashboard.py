import mortgage_calculator as mc
import plotly.express as px
import streamlit as st
import numpy as np


params = dict()
params['price'] = st.sidebar.slider('Price: ', 0, 10_000_000, value=700_000, step=50_000)
percent_of_price = st.sidebar.checkbox('Donwnpayment as percentage', value=True)
if percent_of_price:
    params['down_payment'] = st.sidebar.number_input('Down Payment Percentage:',
                                                     5,
                                                     40,
                                                     value=10,
                                                     step=5) * params['price'] /100
else:
    params['down_payment'] = st.sidebar.slider('Down Payment Amount: ',
                                               35_000,
                                               params['price'] // 2,
                                               value=70_000,
                                               step=5000)
params['utility'] = st.sidebar.number_input('Utility (Per Month)', 100, 3000, value=600, step=50)
params['apr'] = st.sidebar.number_input('APR', 0.5, 10.0, value=5.5, step=0.25)/100
params['ammortization'] = st.sidebar.selectbox('Ammortization Period (Years)',
                                               list(range(10, 36, 5)),
                                               index=3)
params['year_freq'] = st.sidebar.selectbox('Payment Frequency',
                                           list(mc.PaymentFre),
                                           format_func=lambda x: str.capitalize(x.name))
#TODO handle appreciation value
params['appreciation'] = 0.04

if st.sidebar.checkbox('I\'ll be saving on rent',
                       help='If you will be living in the property and you will stop paying rent.'):
    params['rent'] = st.sidebar.number_input('Rent amount', 1_000, 10_000, value=2_400, step=100)
else:
    params['rent'] = 0


params['rent_increment'] = 1.025
params['utility_increment'] = 1.02

df = mc.mortgage_balance_calculator(params)
mortgage_payment = df.loc[1, 'Mortgage Payment']

st.write(f'Payment amount: {mortgage_payment}')

# if st.button('Save to file'):
#     df.to_excel('sample.xlsx')


### Line chart comparing cumulative costs and benefits
fig_cost_benefit = px.line(df,
                           x='Period',
                           y=['Costs Cumulative', 'Profit and Liquidity'],
                           title='Cost and Benefit (Breakeven)',
                           )

st.plotly_chart(fig_cost_benefit)


### Bar chart showing the balance of the whole adventure
fig_cost_benefit_diff = px.bar(
                           x=df['Period'],
                           y= df['Profit and Liquidity'] - df['Costs Cumulative'],
                           title='Balance',
                           labels={'y': 'Balance (Cost - Benefit)', 'x': 'Period'}
                           )
fig_cost_benefit_diff.update_traces(marker_color=np.where(df['Profit and Liquidity'] - df['Costs Cumulative'] < 0, 'red', 'green'))
st.plotly_chart(fig_cost_benefit_diff)


### Area chart for rolling sume of costs ###
fig_rolling_cost = px.area(df,
                           x='Period',
                           y=['Utility Paid Cumulative', 'Interest Paid Cumulative'],
                           title='Rolling sum of costs',
                           )
# Updating the labels since mutiple values is not supported by labels attribute
new_labels={
            'Utility Paid Cumulative': 'Utility',
            'Interest Paid Cumulative': 'Interest',
            }
fig_rolling_cost.for_each_trace(lambda x: x.update(name=new_labels.get(x.name)))
st.plotly_chart(fig_rolling_cost)



fig_payment_breakdown = px.area(df,
                                x='Period',
                                y='Interest Ratio',
                                title='Ratio of Interest on each Mortgage Payment',
                                labels={'Period': 'Period', 'Interest Ratio': 'Interest (%)'}
                                )
st.plotly_chart(fig_payment_breakdown)

# st.line_chart(df, x='Period', y='Costs Paid Cumulative')
st.dataframe(df)
