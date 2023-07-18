import mortgage_calculator as mc
import plotly.express as px
import plotly.graph_objects as go
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


col1, col2 = st.columns(2)
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

#TODO: Send to calculations if possible
summary_values = {
    'Down Payment Amount': params['down_payment'],
    'Mortgage Payment amount': df.iloc[1]['Mortgage Payment'],
    'Number of Payments': df.iloc[-1]['Period'],
    'Total Interest': df.iloc[-1]['Interest Paid Cumulative'],
    'Total Utility': df.iloc[-1]['Utility Paid Cumulative'],
    'Total Property Tax': df['Property Tax'].sum(),
    'Closing Fee': params['price'] * mc.CLOSING_FEE,
    'Down Payment Opportunity Cost': df['Investment Loss'].sum(),
    'Property Value': params['price'],
    'Rent Saved': df.iloc[-1]['Rent Save Cumulative'],
    'Total Cost': df.iloc[-1]["Costs Cumulative"],
    'Total Savings & Equity': df.iloc[-1]["Profit and Liquidity"],
    'Balance': df.iloc[-1]["Profit and Liquidity"] - (df.iloc[-1]["Costs Cumulative"] + params['price'] * mc.CLOSING_FEE),
}

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.markdown(':red[**Total Costs:**]')
        st.markdown(':green[**Total Savings & Equity:**]') 
        st.markdown(':blue[**Balance:**]')
        st.markdown(':orange[**Required Appreciation:**]')
    with col1_2:
        st.markdown(f'{summary_values["Total Cost"]:,}')
        st.markdown(f'{summary_values["Total Savings & Equity"]:,}')
        st.markdown(f'{summary_values["Balance"]:,.2f}')
        st.markdown(f'{(summary_values["Total Savings & Equity"] - summary_values["Total Cost"])*(-100) / params["price"] if summary_values["Balance"] < 0 else 0:,.2f} %', 
                    help="The property price appreciation required to breakeven (Capital Gain Tax not included!)")

    


with col2:
    _, col2_1, _ = st.columns([.2, .7, .1])
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
                    height=495)
    

# row2_c1, row2_c2, row2_c3 = st.columns([.2, .7, .1])
# row2_c1 = st.empty()
# row2_c3 = st.empty()
# with row2_c2:
# Balance Bar Chart
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
st.plotly_chart(fig_cost_benefit_diff, use_container_width=True)
#\ Balance Bar Chart

# if st.button('Save to file'):
#     df.to_excel('sample.xlsx')

col_left, col_right = st.columns([0.5, 0.5])

with col_left:
    # Rolling cost breakdown Graph
    fig_rolling_cost = go.Figure()
    fig_rolling_cost.add_trace(go.Scatter(
        name='Closing Fee',
        x=df['Period'],
        y=[params['price'] * mc.CLOSING_FEE]*len(df),
        stackgroup='one',
        line=dict(color='#9ce82c')
    ))
    fig_rolling_cost.add_trace(go.Scatter(
        name='Lost Investment Opportunity',
        x=df['Period'],
        y=df['Investment Loss'].cumsum(),
        stackgroup='one',
        line=dict(color='#E8df2c')
    ))
    fig_rolling_cost.add_trace(go.Scatter(
        name='Property Tax',
        x=df['Period'],
        y=df['Property Tax'].cumsum(),
        stackgroup='one',
        line=dict(color='#Ff8700')
    ))
    fig_rolling_cost.add_trace(go.Scatter(
        name='Utility & Maintenance',
        x=df['Period'],
        y=df['Utility Paid Cumulative'],
        stackgroup='one',
        line=dict(color='#96121b')
    ))
    fig_rolling_cost.add_trace(go.Scatter(
        name='Interest',
        x=df['Period'],
        y=df['Interest Paid Cumulative'],
        stackgroup='one',
        line=dict(color='#2b165c')
    ))
    fig_rolling_cost.update_layout(
        title='Rolling Cost Breakdown',
    )
    

    st.plotly_chart(fig_rolling_cost)
    #\ Rolling cost breakdown Graph

with col_right:
    # Rolling Savings & Equity Breakdown
    fig_rolling_save = go.Figure()
    fig_rolling_save.add_trace(go.Scatter(
        name='Equity in porperty',
        x=df['Period'],
        y=df['Principal Paid'].cumsum(),
        stackgroup='one',
        line=dict(color='green')
    ))
    fig_rolling_save.add_trace(go.Scatter(
        name='Rent Saved',
        x=df['Period'],
        y=df['Rent'].cumsum(),
        stackgroup='one',
        line=dict(color='lightgreen')
    ))
    fig_rolling_save.update_layout(
        title='Rolling Savings Breakdown'
    )
    st.plotly_chart(fig_rolling_save)


    #\ Rolling Savings & Equity Breakdown

with col_left:
    fig_payment_breakdown = px.area(df,
                                    x='Period',
                                    y='Interest Ratio',
                                    title='Ratio of Interest on each Mortgage Payment',
                                    labels={'Period': 'Period', 'Interest Ratio': 'Interest (%)'}
                                    )
    st.plotly_chart(fig_payment_breakdown)




#TODO: Remove raw dataframe from view
# st.dataframe(df)
