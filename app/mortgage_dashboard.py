import mortgage_calculator as mc
import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd


st.set_page_config(page_title="Mortgage Balance", layout="wide")


params = dict()
params['price'] = st.sidebar.number_input('Price', 0, 10_000_000, value=700_000, step=50_000)
percent_of_price = st.sidebar.checkbox('Donwnpayment as percentage', value=True)
if percent_of_price:
    params['down_payment'] = st.sidebar.number_input('Down Payment Percentage:',
                                                     5,
                                                     40,
                                                     value=10,
                                                     step=5) * params['price'] /100
else:
    params['down_payment'] = st.sidebar.number_input('Down Payment Amount',
                                               35_000,
                                               params['price'] // 2,
                                               value=70_000,
                                               step=5000)
params['utility'] = st.sidebar.number_input('Utility & Maintenance (Per Month)', 100, 3000, value=800, step=50)
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
                       value=True,
                       help='If you will be living in the property and you will stop paying rent.'):
    params['rent'] = st.sidebar.number_input('Rent amount', 1_000, 10_000, value=2_400, step=100)
else:
    params['rent'] = 0


params['rent_increment'] = 1.025
params['utility_increment'] = 1.02
main_df = mc.mortgage_balance_calculator(params)


col1, col2, _ = st.columns(3)
with col1:
    st.title('Mortgage or Rent?')
    st.markdown("""
            With higher interest rates, are you wondering if it makes sense to keep on renting or buy a house and move in? 
            Want to now in short to mid term what amount of property appreciation is going to cover the costs and make buying a propery a sound investment?
            Enter the values based on your situation on the side bar to get an overview of the numbers. 

            **You can select a point in mortgage term to see the situation at the end of that year.**
            """)
    selected_period = st.slider('Show calculations up to year:',
                                min_value=1,
                                max_value=params['ammortization'],
                                value=params['ammortization'],
                                step=1)


df = main_df[main_df['Period'] <= selected_period * params['year_freq'].value]
summary_values = {
    'Mortgage Payment amount': df.iloc[1]['Mortgage Payment'],
    'Number of Payments': df.iloc[-1]['Period'],
    'Total Interest': df.iloc[-1]['Interest Paid Cumulative'],
    'Total Utility': df.iloc[-1]['Utility Paid Cumulative'],
    'Total Property Tax': df['Property Tax'].sum(),
    'Closing Fee': params['price'] * mc.CLOSING_FEE,
    'Down Payment Opportunity Cost': df['Investment Loss'].sum(),
    'Property Value': params['price'],
    'Rent Saved': df.iloc[-1]['Rent Save Cumulative'],
}

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.markdown(':red[**Total Costs:**]')
        st.markdown(':green[**Total Savings & Value:**]') 
    with col1_2:
        st.markdown(f'{df.iloc[-1]["Costs Cumulative"]:,}')
        st.markdown(f'{df.iloc[-1]["Profit and Liquidity"] + summary_values.get("Closing Fee"):,}')
    


with col2:
    _, col2_1, _ = st.columns([.25, .5, .25])
    with col2_1:
        st.subheader('Summary')
        summary = pd.DataFrame(index=summary_values.keys(), data=summary_values.values(), columns=['Value (CAD)'])


        def highlighter(s):
            if s.name == 'Total Cost':
                return ["color: red"] * len(s)
            elif s.name == 'Total Value':
                return ["color: green"] * len(s)
            else:
                return [""] * len(s)

        st.dataframe(summary.style.format('{:,.0f}')
                    .apply(highlighter, axis=1),
                    height=425)


# summary_md =f"""
#     |Item| Value (CAD)|
#     |----|----|
#     |Mortgage Payment amount| {int(df.iloc[1]['Mortgage Payment'])}|
#     |Number of Payments| {int(df.iloc[-1]['Period'])}|
#     |Total Interest| {int(df.iloc[-1]['Interest Paid Cumulative'])}|
#     |Total Utility| {int(df.iloc[-1]['Utility Paid Cumulative'])}|
#     |Total Property Tax| {int(df['Property Tax'].sum())}|
#     |Closing Fee| {int(params['price'] * mc.CLOSING_FEE)}|
#     |Down Payment Opportunity Cost| {int(df['Investment Loss'].sum())}|
#     |:red[**Total Cost**]| PLACEHOLDER | 
#     |Property Value| {int(params['price'])}|
#     |Rent Saved| {int(df.iloc[-1]['Rent Save Cumulative'])}|
#     |:green[**Total Value**]| PLACEHOLDER|
    
# """   

# st.markdown(summary_md)


# if st.button('Save to file'):
#     df.to_excel('sample.xlsx')

col_left, col_right = st.columns([0.5, 0.5])

with col_left:
    ### Line chart comparing cumulative costs and benefits
    fig_cost_benefit = px.line(df,
                            x='Period',
                            y=['Costs Cumulative', 'Profit and Liquidity'],
                            title='Cost and Benefit (Breakeven)',
                            )

    st.plotly_chart(fig_cost_benefit)

with col_right:
    ### Bar chart showing the balance of the whole adventure
    fig_cost_benefit_diff = px.bar(
                            x=df['Period'],
                            y= df['Profit and Liquidity'] - (df['Costs Cumulative'] + params['price'] * mc.CLOSING_FEE),
                            title='Balance',
                            labels={'y': 'Balance (Cost - Benefit)', 'x': 'Period'}
                            )
    fig_cost_benefit_diff.update_traces(
        marker_color=np.where(
            df['Profit and Liquidity'] - (df['Costs Cumulative'] + params['price'] * mc.CLOSING_FEE) < 0, 
            'red', 
            'green')
            )
    st.plotly_chart(fig_cost_benefit_diff)

with col_left:
    ### Area chart for rolling sume of costs ###
    fig_rolling_cost = px.area(df,
                            x='Period',
                            y=['Utility Paid Cumulative', 'Interest Paid Cumulative'],
                            title='Costs Breakdown',
                            )
    # Updating the labels since mutiple values is not supported by labels attribute
    new_labels={
                'Utility Paid Cumulative': 'Utility',
                'Interest Paid Cumulative': 'Interest',
                }
    fig_rolling_cost.for_each_trace(lambda x: x.update(name=new_labels.get(x.name)))
    st.plotly_chart(fig_rolling_cost)


with col_right:
    fig_payment_breakdown = px.area(df,
                                    x='Period',
                                    y='Interest Ratio',
                                    title='Ratio of Interest on each Mortgage Payment',
                                    labels={'Period': 'Period', 'Interest Ratio': 'Interest (%)'}
                                    )
    st.plotly_chart(fig_payment_breakdown)

# st.line_chart(df, x='Period', y='Costs Paid Cumulative')

#TODO: Remove raw dataframe from view
st.dataframe(df)
