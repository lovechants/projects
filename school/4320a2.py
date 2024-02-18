# Loading in the data
# https://www.kaggle.com/datasets/justinpakzad/ssense-fashion-dataset?resource=download
import pandas as pd
import numpy as np
data = "~/Documents/School/data/ssense_dataset.csv"
df = pd.read_csv(data)
#print(df.head()) 

# import graphing libraries 
import matplotlib.pyplot as plt 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=("One quantitative: Price Statistics",
                    "One qualitative: Brand Frequency",
                    "One qualitative and one quantitative: Descriptive Statistics with Boxplots",
                    "Plot 4",
                    "Plot 5"))
#1. Visualization of a single quantitative data variable.
# Price Histogram
fig.add_trace(go.Box(   # Draw onto our canvas, create a boxplot 
    x = df["price_usd"], # x to make it horizontal 
    name = "Price", 
    boxpoints = False, # Whiskers only plot 
    line_color = 'rgb(0,0,0)', 
), row = 1, col = 1)
fig.update_layout(
    #title='Price in USD of SSENSE Data',
    yaxis=dict(
        autorange=True, 
        showgrid=False, # Removing elements in regards to Tufte 
        zeroline=False,
        gridcolor='rgb(255, 255, 255)', # white grid 
        gridwidth=.5,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    paper_bgcolor='rgb(255, 255, 255)', # white background 
    plot_bgcolor='rgb(255, 255, 255)',
    showlegend=False
)
#fig.update_yaxes(title_text = "Frequency", showgrid = False, row = 1, col = 1)i
#2. Visualization of a single qualitative 
# Brand Frequency Bar Chart 

brands = sorted(list(set(df["brand"])))
#print(brands)
count = df['brand'].value_counts()
fig.add_trace(go.Bar(x=brands,y = count, name = ""), row =1, col = 2) # name to remove trace1 on hover 

# 3. Visualization of a single qualitative and quantitative variable
# using variables from previously created visualizations 
for brand in brands:
    boxplot_data = df[df['brand'] == brand]['price_usd']
    fig.add_trace(go.Box(y=boxplot_data, name = brand, boxpoints=False), row=1, col=3)

fig.update_layout(
    title='Boxplot of Prices for Each Brand',
    xaxis_title='Brand',
    yaxis_title='Price (USD)'
)
# 4. Visualization representing more than 2 data 

types = list(set(df['type']))
print(types)
num_desc = df['description'].value_counts() 
# TODO Create a new column in the data categorizing based on popular categories
#  TODO restart
print(num_desc)
#fig.show()
