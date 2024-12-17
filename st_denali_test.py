import numpy as np
import pandas as pd
import streamlit as st


def offset_value_per_cow(offset_price, mitigation_pct, baseline_CH4 = 300, GWP=28, interval='daily'):
    value_per_cow = offset_price * 28*1e-6 * baseline_CH4 * mitigation_pct*.01

    if interval=='daily':
        return value_per_cow
    if interval == 'annual':
        return 365*value_per_cow

    try:
        return interval*value_per_cow # this is the sort of dynamic typing that makes programmers sad pandas
    except:
        return 0

gwp = 28

st.subheader('Enteric Methane Reducing Product Value Calculator')
st.write('If using mobile, click > symbol to change settings')
st.write('')

with st.sidebar:    
    xaxis= st.selectbox("X-Axis Variable", 
        ['Methane Reduction (%)', "Carbon Offset Price"])

    if xaxis != 'Methane Reduction (%)':
        mitigation_pct = st.number_input(
            label = 'Methane Reduction (%)', value =25)
    if xaxis != "Carbon Offset Price":
        offset_price = st.number_input(
            label = 'Price of Carbon ($/tCO2)', value=40)
    baseline = st.number_input(
        label='Baseline CH4 (g per cow daily)',value=300)
    interval = st.radio(label='Daily or Annual Value', options=['daily', 'annual'])
  
    q_prod = st.checkbox("Productivity Increased?")
    if q_prod == True:
        milk_price = st.number_input('Milk price ($/liter)', 0.50)
        milk_production = st.number_input('Daily Milk produced (liter)', 4)
        boost = st.number_input('Productivity Boost from Intervention (%)', 0)


added_value =0
if q_prod == True:
    if interval == 'daily':
        added_value = boost*milk_price*milk_production*.01
    if interval == 'annual':
        added_value =  boost*milk_price*milk_production*.01 * 365



offset_price_range = np.arange(101)
mitigation_pct_range = np.arange(101)


results = []
if xaxis=='Carbon Offset Price':
    for offset_p in offset_price_range:
        offset_value = offset_value_per_cow(offset_p,
                    mitigation_pct, baseline, interval=interval, GWP=gwp)

        results.append({
            'Offset Price ($/t_CO2)' : offset_p,
            'Methane Reduction (%)': mitigation_pct,
            'Baseline (g CH4 per day)':baseline,
            'GWP': gwp,
            'Interval': interval,
            'Offset Value ($)': offset_value,
            'Added Production Value ($)': added_value,
            'Total Value ($)': added_value+offset_value,
        })


    df = pd.DataFrame(results)

    if q_prod != True:
        st.line_chart(data=df, x='Offset Price ($/t_CO2)',
                            y='Offset Value ($)')

    if q_prod == True:
        st.line_chart(data=df, x='Offset Price ($/t_CO2)',
                            y=['Offset Value ($)',
                            'Added Production Value ($)',
                            'Total Value ($)'], y_label = 'Value ($)')





results = []
if xaxis == "Methane Reduction (%)":
    for mitigation_pct in mitigation_pct_range:
        offset_value = offset_value_per_cow(offset_price,
                    mitigation_pct, baseline, interval=interval, GWP=gwp)

        results.append({
            'Offset Price ($/t_CO2)' : offset_price,
            'Methane Reduction (%)': mitigation_pct,
            'Baseline (g CH4 per day)':baseline,
            'GWP': gwp,
            'Interval': interval,
            'Offset Value ($)': offset_value,
            'Added Production Value ($)': added_value,
            'Total Value ($)': added_value+offset_value,
        })


    df = pd.DataFrame(results)

    if q_prod != True:
        st.line_chart(data=df, x='Methane Reduction (%)',
                            y='Offset Value ($)')

    if q_prod == True:
        st.line_chart(data=df, x='Methane Reduction (%)',
                            y=['Offset Value ($)',
                            'Added Production Value ($)',
                            'Total Value ($)'], y_label = 'Value ($)')


st.write('[tbd] write discussion of plot here')
