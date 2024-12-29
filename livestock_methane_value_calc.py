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

st.markdown('''
        Written by [Dr. Denali R. "Doc" Brown](https://linkedin.com/in/heydocbrown).      
        Email: <doc@cowbell-labs.org>  
        Substack: [cowbell-climate.substack.com](https://cowbell-climate.substack.com)''')

st.write('If on your phone, click > symbol on the left to change settings')


with st.sidebar:    
    system = st.selectbox('Livestock System', system_list)
    methane_val = livestock_methane_year[system] / 365 * 1000
    baseline = st.number_input(label='Baseline CH4 (g per cow daily)', value=methane_val)

    xaxis = st.selectbox("X-Axis Variable", ['Methane Reduction (%)', 
                                             "Carbon Offset Price ($ per ton CO2)"])

    mitigation_pct = st.number_input(label='Methane Reduction (%)', value=25) if xaxis != 'Methane Reduction (%)' else 25
    offset_price = st.number_input(label='Price of Carbon ($/tCO2)', value=40) if xaxis != "Carbon Offset Price ($ per ton CO2)" else 25

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
 

if xaxis == 'Carbon Offset Price':
    alt_ax = alt.Axis(format='$,.2f')
else:
    alt_ax=alt.Axis()

chart = alt.Chart(df.reset_index()).transform_fold(
    y_columns, 
    as_=['Metric', 'Value']
).mark_line().encode(
    x=alt.X('index:Q', title=xaxis, axis=alt_ax),
    y=alt.Y('Value:Q', title='Value ($) ' + interval, axis=alt_ax),
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
st.subheader('Discussion')
st.write('''
         As a reference publicly stated cost anti-methane products such as Bovaer 
         and Bromoform (Red Seaweed) vary between \$0.50 and \$1.00 per milk cow per day. 
         Livestock that eats less - e.g. smaller animals - will use less. 
         This calculator suggests those costs are not supported by any realistic carbon price. 
         The intervention would need to increase productivty substantially at those costs. The evidence for that is 
         inconsistent today. And even then there'd be little profit for the farmer at cost of 
         \$0.50 per per day and only an actual loss at \$1.00 per day. If a farmer could get a premium 
         price on their milk, that would support these costs. Even a 10 cent premium per liter would 
         be worth $2.50 per cow per day for an average US dairy cow.   
         ''')  

st.subheader('How to use this calculator.')
st.write('This calculator estimates the value created by an anti-methane intervention.')
text ='''
#1 Select your daily methane production baseline.
* Method 1: Pick a livestock system and it will auto-fill the daily methane production.  
* Method 2: Manually enter a value into the Baseline CH4.  

#2 Choose what you want for the x-axis of the plot.
* Option 1: Carbon Offset Price.   
* Option 2: Methane Reduction from an intervention"

#3 Enter a constant value for the variable not on the x-axis.
* Carbon Offset Price defaults to the Danish Livestock Methane Tax
* Methane Reduction defaults to the effect of Bovaer on Dairy

#4 Choose if the y-axis shows daily or annual value created.

#5 [Optional] Select a milk production increase.
* Meat production will be added later.
* Be reasonable: methane uses ~6\% of cattle calories. 
* Set a price of milk
** \$0.50 per liter is reasonable which is $22 per hundred weight.
* Select a daily milk prduction
  * 4-5 liters is reasonable for smallholder farms.
  * 25 liters is average in the United States
'''

st.markdown(text)

st.subheader('This is a simple calculator for quick evaluation.')
text = '''
This calculator is intened as starting point for a funder.  

A more complex calculator would for a business would include the embodied carbon of the intervention, as well as the cost of labor, 
the cost of sales, and so forth.  

A livestock calculator aimed at helping a farmer figure out their financial benefit would 
incorporate more specific feed scenarios and calculate methane from that. For an example of that,
look at AgNext Colorado State University beef feedlot methane calculator (https://agnext.colostate.edu/beef-fact/). 
I used that calculator to check that this was accuate.
'''

st.markdown(text)

st.subheader('Sources')
st.markdown('''Methane by US system provided by Charles Brooke from 
           [1](https://www.epa.gov/system/files/documents/2024-02/us-ghg-inventory-2024-chapter-5-agriculture.pdf)
           and [2, Table A179](https://www.epa.gov/sites/default/files/2020-04/documents/us-ghg-inventory-2020-annex-3-additional-source-or-sink-categories-part-b.pdf).
            ''')
st.markdown('''
            Kenyan Methane emissions estimated from productivity and
            [Gerber et. al 2011](https://www.sciencedirect.com/science/article/abs/pii/S1871141311000953)
            ''')
st.markdown('''
            Publically stated prices of anti-methane feed additives 
            * [DSM Bovaer \$0.50 per day target](https://www.abc.net.au/news/2023-02-26/how-science-is-slashing-methane-from-cow-burps/101968484)  
            * [SeaForest Bromofrom sub-\$1.00 per day target](https://www.beefcentral.com/carbon/are-methane-reducing-additives-palatable-for-lotfeeders/)  
            * [Seastock Bromform \$0.50 per day target](https://agfundernews.com/methane-busting-feed-supplements-are-beginning-to-scale-but-who-will-foot-the-bill-and-what-will-drive-widespread-adoption)  
            * [Rumin8 Bromofrom bolus $0.27 per day target](https://www.abc.net.au/news/2023-02-26/how-science-is-slashing-methane-from-cow-burps/101968484)
            ''')