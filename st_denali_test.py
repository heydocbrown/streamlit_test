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


offset_price_range = np.arange(101)
mitigation_pct = st.number_input(
    label = 'Methane Reduction (%)', value =25)

baseline = st.number_input(
    label='Baseline CH4 (g per cow daily)',value=300)
interval = 'daily'

interval = st.radio(label='Daily or Annual Value', options=['daily', 'annual'])

gwp = 28

milk_price = st.number_input('Milk price ($/liter)', 0.50)
milk_production = st.number_input('Daily Milk produced (liter)', 4)
boost = st.number_input('Productivity Boost from Intervention (%)', 0)

if interval == 'daily':
    added_value = boost*milk_price*milk_production*.01
if interval == 'annual':
    added_value =  boost*milk_price*milk_production*.01 * 365

results = []

for offset_p in offset_price_range:
    offset_value = offset_value_per_cow(offset_p,
                mitigation_pct, baseline, interval=interval, GWP=gwp)

    results.append({
        'Offset Price ($/t_CO2)' : offset_p,
        '% Reduction': mitigation_pct,
        'Baseline (g CH4 per day)':baseline,
        'GWP': gwp,
        'Interval': interval,
        'Offset Value ($)': offset_value,
        'Added Production Value ($)': added_value,
        'Total Value ($)': added_value+offset_value,
    })


df = pd.DataFrame(results)

st.line_chart(data=df, x='Offset Price ($/t_CO2)',
                     y='Offset Value ($)')


st.line_chart(data=df, x='Offset Price ($/t_CO2)',
                     y=['Offset Value ($)',
                     'Added Production Value ($)',
                     'Total Value ($)'])



mitigation_pct_range = np.arange(101)
offset_price = st.number_input(
    label = 'Price of Carbon ($/tCO2)', value=40)


results = []

for mitigation_pct in mitigation_pct_range:
    offset_value = offset_value_per_cow(offset_price,
                mitigation_pct, baseline, interval=interval, GWP=gwp)

    results.append({
        'Offset Price ($/t_CO2)' : offset_price,
        '% Reduction': mitigation_pct,
        'Baseline (g CH4 per day)':baseline,
        'GWP': gwp,
        'Interval': interval,
        'Offset Value ($)': offset_value,
        'Added Production Value ($)': added_value,
        'Total Value ($)': added_value+offset_value,
    })


df = pd.DataFrame(results)

st.line_chart(data=df, x='% Reduction',
                     y='Offset Value ($)')


st.line_chart(data=df, x='% Reduction',
                     y=['Offset Value ($)',
                     'Added Production Value ($)',
                     'Total Value ($)'])
