import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

livestock_methane_year = {
    "US DAIRY: Cows": 147.4,
    "Kenya DAIRY: Cows (low)":50,
    "Kenya DAIRY: Cows (high)":109, 
    "US DAIRY: Calves": 12.2,
    "US DAIRY: Replacements 7–11 months": 45.6,
    "US DAIRY: Replacements 12–23 months": 68.8,
    "US BEEF: Bulls": 98.0,
    "US BEEF: Calves": 10.5,
    "US BEEF: Cows": 94.7,
    "US BEEF: Replacements 7–11 months": 60.4,
    "US BEEF: Replacements 12–23 months": 69.8,
    "US BEEF: Steer Stockers": 58.0,
    "US BEEF: Heifer Stockers": 60.2,
    "US BEEF: Total Feedlot": 43.0,
    "US Sheep": 8.0,
    "US Horses": 18.0,
    "US Swine": 1.5,
    "US Goats": 5.0,
    "US American Bison": 82.2,
    "US Mules and Asses": 10.0
}
system_list = list(livestock_methane_year.keys())

def offset_value_per_cow(offset_price, mitigation_pct, baseline_CH4 = 300, GWP=28, interval='daily'):
    value_per_cow = offset_price * 28*1e-6 * baseline_CH4 * mitigation_pct*.01

    if interval=='per day':
        return value_per_cow
    if interval == 'per year':
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
    system = st.selectbox('Livestock System', system_list)
    methane_val = livestock_methane_year[system] / 365 * 1000

    xaxis = st.selectbox("X-Axis Variable", ['Methane Reduction (%)', "Carbon Offset Price"])

    mitigation_pct = st.number_input(label='Methane Reduction (%)', value=25) if xaxis != 'Methane Reduction (%)' else None
    offset_price = st.number_input(label='Price of Carbon ($/tCO2)', value=40) if xaxis != "Carbon Offset Price" else None

    baseline = st.number_input(label='Baseline CH4 (g per cow daily)', value=methane_val)
    interval = st.radio(label='Daily or Annual Value', options=['per day', 'per year'])

    q_prod = st.checkbox("Milk Productivity Increased?")
    if q_prod:
        milk_price = st.number_input('Milk price ($/liter)', 0.50)
        milk_production = st.number_input('Daily Milk produced (liter)', 4)
        boost = st.number_input('Productivity Boost from Intervention (%)', 0)

added_value = 0
if q_prod:
    added_value = boost * milk_price * milk_production * 0.01 * (365 if interval == 'annual' else 1)

offset_price_range = np.arange(101)
mitigation_pct_range = np.arange(101)

results = []
x_values = offset_price_range if xaxis == 'Carbon Offset Price' else mitigation_pct_range
x_label = 'Offset Price ($/t_CO2)' if xaxis == 'Carbon Offset Price' else 'Methane Reduction (%)'

for x in x_values:
    offset_p = x if xaxis == 'Carbon Offset Price' else offset_price
    mitigation_p = mitigation_pct if xaxis == 'Carbon Offset Price' else x
    offset_value = offset_value_per_cow(offset_p, mitigation_p, baseline, interval=interval, GWP=gwp)
    results.append({
        'Offset Price ($/t_CO2)': offset_p,
        'Methane Reduction (%)': mitigation_p,
        'Baseline (g CH4 per day)': baseline,
        'GWP': gwp,
        'Interval': interval,
        'Offset Value ($)': offset_value,
        'Added Production Value ($)': added_value,
        'Total Value ($)': added_value + offset_value,
    })

df = pd.DataFrame(results)
y_columns = ['Offset Value ($)'] if not q_prod else ['Offset Value ($)', 'Added Production Value ($)', 'Total Value ($)']
 

chart = alt.Chart(df.reset_index()).transform_fold(
    y_columns, 
    as_=['Metric', 'Value']
).mark_line().encode(
    x=alt.X('index:Q', title='Offset Price ($/t_CO2)'),
    y=alt.Y('Value:Q', title='Value ($) ' + interval),
    color=alt.Color('Metric:N', title='Metrics',
                    legend=alt.Legend(orient='top-left', title='Metrics'))
).properties(
    width='container'
).configure_axis( 
    labelFontSize=16, 
    titleFontSize=18, 
    tickSize=10)


# Display Altair chart in Streamlit
st.altair_chart(chart, use_container_width=True)
