import pandas as pd
import numpy as np
import plotly.graph_objs as go

# Use this file to read in your data and prepare the plotly visualizations. The path to the data files are in
# `data/file_name.csv`
def prepdata(dataset='data/missile_attacks_daily.csv'):
    df=pd.read_csv(dataset)
    #print("Deployed data preview:\n", df.head())
    # means of attack
    df['model_group'] = df['model'].replace({
    'Orlan-10': 'Other drones',
    'X-59': 'X-59/X-69',
    'Lancet': 'Other drones',
    'Unknown UAV': 'Other drones',
    'Iskander-M/KN-23': 'Iskander',
    'Iskander-M': 'Iskander',
    'Iskander-K': 'Iskander',
    'Merlin-VR': 'Other drones',
    'Supercam': 'Other drones',
    'ZALA': 'Other drones',
    'Reconnaissance UAV': 'Other drones',
    'C-300': 'C-300/C-400',
    'X-101/X-555 and Kalibr': 'X-101/X-555',
    'X-101/X-555 and Kalibr and Iskander-K': 'X-101/X-555',
    'X-101/X-555 and Kalibr and X-59/X-69': 'X-101/X-555',
    'X-101/X-555 and X-22 and Kalibr': 'X-101/X-555',
    'Iskander-M and Iskander-K': 'Iskander',
    'C-300/C-400 and Iskander-M': 'C-300/C-400',
    'C-400 and Iskander-M': 'C-300/C-400',
    'X-101/X-555 and Kalibr and X-59/X-69': 'X-101/X-555',
    'X-22': 'X-22/X-32',
    'X-22 and X-32': 'X-22/X-32',
    'X-101/X-555 and Kalibr and Iskander-M/KN-23': 'Kalibr'})
    # Cost of war
    weapon_prices = {
    "Shahed-136/131": 0.05,
    "X-101/X-555": 13.0,
    "Other drones": 0.2,
    "X-59/X-69": 0.5,
    "Iskander": 3.0,
    "C-300/C-400": 1.2,
    "Kalibr": 6.5,
    "X-22/X-32": 1.0,
    "X-47 Kinzhal": 10.0,
    "Other models":0.05}
    df['weapon_price'] = df['model_group'].map(weapon_prices).fillna(0)
    df['cost_of_attack'] = df['weapon_price'] * df['launched']
    #df['year']=pd.to_datetime(df['time_start'], format='%Y-%m-%d %H:%M', errors='coerse').dt.year
    df['year'] = pd.to_datetime(df['time_start'], errors='coerce').apply(lambda x: x.year if pd.notnull(x) else None)

    #df['year']=df['year'].replace({2025:'Q1 2025'})
    #df['year']=df['year'].astype(str)
    #from pandas.api.types import CategoricalDtype
    #year_order=CategoricalDtype(categories=['2022','2023','2024','Q1 2025'],ordered=True)
    #df['year']=df['year'].astype(year_order)
    #print(df['year'].unique())
    df['time_start']=pd.to_datetime(df['time_start'], errors='coerce')
    df['day']=df['time_start'].dt.date
    df['month']=df['time_start'].dt.to_period('M').dt.to_timestamp()

    return df



def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    # first chart plots arable land from 1990 to 2015 in top 10 economies
    # as a line chart
    #####Chart 1 - number of aerial attacks per year
    graph_one = []
    df=prepdata()
    attacks_per_annum=pd.DataFrame(df.groupby('month').size()).reset_index()
    attacks_per_annum.columns=['period','quantity']
    graph_one.append(
      go.Bar(
      x = attacks_per_annum['period'],
      y = attacks_per_annum['quantity'],
      marker_color='rgb(64, 60, 45)'
      )
    )

    layout_one = dict(title = 'Number of aerial attacks',
                xaxis = dict(title = '<i>Select period</i>', type='date', rangeselector=dict(
                buttons=[
                dict(count=6, label='6m', step='month', stepmode='backward'),
                dict(count=1, label='1y', step='year', stepmode='backward'),
                dict(step='all')
                ]
                ),
                rangeslider=dict(visible=True),
                ),
                yaxis = dict(title = '# of attacks launched'),
                #height=350,
                margin=dict(l=60, r=20, b=50, t=100, pad=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',   # chart area background

                )

# Chart 2 - Type of weapons launched
    graph_two = []
    df=prepdata()
    # Group by year and model_group
    grouped = df.groupby(['year', 'model_group'])['launched'].sum().reset_index()

    # Get top 9 model groups across all years
    top_models = df.groupby('model_group')['launched'].sum().sort_values(ascending=False)[:9].index.tolist()

    # Replace all other models with 'Other models'
    grouped['model_group'] = grouped['model_group'].apply(lambda x: x if x in top_models else 'Other models')

    # Re-group after collapsing 'other models'
    grouped = grouped.groupby(['year', 'model_group'])['launched'].sum().reset_index()

    # Pivot to wide format for plotting
    pivot = grouped.pivot(index='year', columns='model_group', values='launched').fillna(0)

    # Add one trace per model_group (stacked)
    for model in pivot.columns:
        graph_two.append(
        go.Bar(x=pivot.index,
            y=pivot[model],
            name=model
        )
    )

    layout_two = dict(
        title='Weapons launched by weapon type',
        barmode='stack',  # <== Important for stacked bars
        xaxis=dict(title=' '),
        yaxis=dict(title='Quantity launched', tickfont=dict(size=9),
               tickvals=[0, 100, 1000, 5000, 10000, 20000, 30000],
               ticktext=['0','100', '1,000', '5,000', '10,000', '20,000', '30,000']),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',   # chart area background
        margin=dict(l=60, r=20, b=50, t=100, pad=10),
        #height=350,
)


# Chart 3 - Air defence effectiveness
    graph_three = []
    df=prepdata()
    objects_destroyed=df.groupby('month')['destroyed'].sum()
    objects_launched=df.groupby('month')['launched'].sum()
    objects_summary = pd.concat([objects_launched, objects_destroyed], axis=1).reset_index()
    objects_summary['effectiveness']=np.round(objects_summary['destroyed']/objects_summary['launched'],2)
    graph_three.append(
      go.Scatter(
      y = objects_summary['effectiveness'],
      x = objects_summary['month'],
      mode = 'lines+markers',
      marker_color='rgb(64, 60, 45)'
      )
    )

    layout_three = dict(title = 'Air deffence effectiveness <br> (as share of destroyed targets)',
                xaxis = dict(title = '<i>Select period</i>', type='date', rangeselector=dict(
                buttons=[
                dict(count=6, label='6m', step='month', stepmode='backward'),
                dict(count=1, label='1y', step='year', stepmode='backward'),
                dict(step='all')
                ]
                ),
                rangeslider=dict(visible=True),
                ),
                yaxis = dict(title = '% of destroyed objects', range=[0,1],),
                #height=350,
                margin=dict(l=60, r=20, b=50, t=100, pad=10),

                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',   # chart area background
                       )

# Attack targets
    graph_four = []
    df = prepdata()
    cities = ['Kyiv', 'Odesa', 'Dnipro', 'Kharkiv', 'Lviv']
    compass = ['north', 'south', 'east', 'east', 'west']

# Create an empty list to store target counts
    targets = []

    # Loop through the cities and compass directions to count the attacks per year
    for city, direction in zip(cities, compass):
        pattern = fr'{city}|Ukraine|{direction}'
        # Group by year and city, and count occurrences of the pattern
        city_targets = df[df['target'].str.contains(pattern, case=False, na=False)]
        yearly_counts = city_targets.groupby('month').size().reset_index(name='attack_count')
        yearly_counts['city'] = city
        targets.append(yearly_counts)

    # Combine all targets for each city into one DataFrame
    targets_of_attack = pd.concat(targets)
    # Define a muted color palette
    muted_colors = [
    'rgb(102, 102, 153)',   # muted purple
    'rgb(153, 153, 102)',   # muted olive
    'rgb(119, 136, 153)',   # muted blue-grey
    'rgb(128, 128, 128)',   # muted grey
    'rgb(160, 82, 45)'      # muted brown
    ]
    # Create the line plot

    for city, color in zip(cities, muted_colors):
        city_data = targets_of_attack[targets_of_attack['city'] == city]
        graph_four.append(go.Scatter(
            x=city_data['month'],
            y=city_data['attack_count'],
            mode='lines+markers',  # Line with markers
            name=city,
            line=dict(color=color),
            marker=dict(color=color))
        )

    layout_four = dict(title = 'Attacks on Ukraine biggest cities',
                xaxis = dict(title = '<i>Select period</i>', type='date', rangeselector=dict(
                buttons=[
                dict(count=6, label='6m', step='month', stepmode='backward'),
                dict(count=1, label='1y', step='year', stepmode='backward'),
                dict(step='all')
                ]
                ),
                rangeslider=dict(visible=True),
                ),
                yaxis = dict(title = 'Number of attacks'),
                #height=350,
                margin=dict(l=60, r=20, b=50, t=100, pad=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',   # chart area background
                )


    #####Chart 5- Cost of attacks
    graph_five = []
    df=prepdata()
    cost_of_war=pd.DataFrame(df.groupby('year')['cost_of_attack'].sum()).reset_index()
    cost_of_war.columns=['year','cost_of_attack']
    graph_five.append(
      go.Bar(
      x = cost_of_war['year'],
      y = cost_of_war['cost_of_attack'],
      marker_color='rgb(64, 60, 45)'
      )
    )

    layout_five = dict(title = dict(text='Cost to russian taxpayer of<br>aerial attacks against Ukraine', x=0.5, xanchor='center'),
                xaxis = dict(title = 'Year', tickvals=cost_of_war['year'].tolist(), ticktext=cost_of_war['year'].astype(str).tolist()),
                yaxis = dict(title = 'cost in mln USD', tickformat=',',),
                #height=350,
                margin=dict(l=100, r=20, b=50, t=100, pad=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',   # chart area background
                #autosize= True

                )
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))

    return figures
