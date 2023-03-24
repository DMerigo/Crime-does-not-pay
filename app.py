import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pathlib

mapbox_access_token = 'pk.eyJ1IjoibWVyaWdvIiwiYSI6ImNsZmxsMWc5cjAyd3UzcXF6bDZuaGJjejIifQ.r3BD-2Lb9v8xxkchyWWVzg'

px.set_mapbox_access_token(mapbox_access_token)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}])


app.title = 'Crime does not Pay'

server = app.server
app.config.suppress_callback_exceptions = True

# Path to dataset

base_path = pathlib.Path(__file__).parent.resolve()
dataset_path = base_path.joinpath('data').resolve()

# Prepare data

crime_data = (
    pd.read_csv(dataset_path.joinpath('processed_communities.csv'), usecols = ['population', 'medIncome', 'violent_crime_rate', 'PctPopUnderPov', 'PctUnemployed', 'state', 'area', 'latitude', 'longitude'])
)

features_trans = {
    'population' : 'Population',
    'medIncome' : 'Median Income',
    'violent_crime_rate' : 'Violent Crime Rate',
    'PctPopUnderPov' : 'Percentage under Poverty Line',
    'PctUnemployed' : 'Percentage Unemployed',
    'state' : 'State'

}

communities_list = crime_data['area'].unique()
states_list = crime_data['state'].unique()
features = ['Population', 'Median Income', 'Violent Crime Rate']
composition = ['Percentage under Poverty Line', 'Percentage Unemployed', 'Racial Composition']
features_correlation = ['Population', 'Median Income', 'Violent Crime Rate', 'Percentage under Poverty Line', 'Percentage Unemployed']

communities_list = np.append(communities_list, 'All')
states_list = np.append(states_list, 'All')

initial_zoom = 3
initial_center = {'lat' : 39.8, 'lon' : 260}
feat_selected = 'violent_crime_rate'

# Define Graphics (Map, Correlation plot, composition)

# map_heat = px.density_mapbox(crime_data, lat='latitude', lon='longitude', z='violent_crime_rate', radius=10,
#                         center = initial_center, zoom= initial_zoom,
#                         color_continuous_scale = 'viridis',
#                         mapbox_style="dark",
#                         hover_data = ['Population', 'Median Income'],
#                         height = 540,
#                         width = 860)


# Control Panel

def app_control():
    """
    The control panel to select the state and community for the main map and community composition
    """

    return html.Div(
        id = 'control_panel',
        style = {'height' : '100%', 'width': '100%'},
        children = [
            html.P('Select State'),
            dcc.Dropdown(id = 'state selection', options = [{'label' : opt, 'value' : opt} for opt in states_list],
                value = 'All',
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.P('Select the Feature to Visualize'),
            dcc.Dropdown(id = 'feature selection', options = [{'label' : features_trans[i], 'value' : i} for i in features_trans], 
                value = 'violent_crime_rate',
            ),
        ],
)

# Explanation of the app

def app_intro():
    """
    This is a description of the App's functions and reasoning
    """

    return html.Div(
        id = 'description_app',
        children = [
        html.H1('Crime Rate in the United States'),
        html.Div(
        id = 'welcome',
        children = ['Welcome to the Crimes Dashboard! Here you can explore the incidence of violent crimes in the continental USA and Alaska. Please feel free to use the State selector to select a specific state and the Feature selector to select the feature to visualize. This data was taken from the UCI database and contains crime information for the year 1995']
        )
        ]
    )

# Define Layout

app.layout = html.Div(
    id = 'my_app',
    children = [
        html.Div(
            id = 'control_area',
            className = 'four columns',
            children = [app_intro(), app_control()]
        ),
        html.Div(
            id = 'map_area',
            className = 'eight columns',
            children = [
                html.Div(
                    id = 'heat_color_map',
                    children = [
                        dcc.Tabs(id = 'tabs', value = 'tab-1',
                                 children = [
                                    dcc.Tab(label = 'Map', value = 'tab-1',
                                        children = [
                                            html.Div([
                                                html.B('Heatmap of Violent Crime Incidence in the United States of America'),
                                                html.Hr(),
                                                dcc.Graph(id = 'actual_map', figure = {})
                                                ])]),
                                    dcc.Tab(label = 'Heatmap', value = 'tab-2',
                                        children = [
                                            html.Div([
                                                html.B('Correlation Map'),
                                                dcc.Graph(id = 'corr_chart', figure = {})
                                                ])]),
                                            ]),
                                            ],
                                            ),
                html.Div(
                    id = 'stacked_bar_section', children = [
                            html.Br(),
                            html.Hr(),
                            html.B('Feature Analysis'),
                            html.Hr(),
                            dcc.Graph(id = 'bar_chart', figure = {})
                        ])
                    ]),
        ],
)


# App callbacks

@app.callback(
    dash.dependencies.Output('actual_map', 'figure'),
    [
        Input('state selection', 'value'),
        Input('feature selection', 'value')
    ])

def update_state(state, feature):
    filtered_data = crime_data
    zoom = initial_zoom
    center = initial_center
    if state != 'All' and state is not None:
        filtered_data = crime_data[crime_data['state'] == state]
        zoom = initial_zoom
    fig = px.density_mapbox(filtered_data,
                            hover_name = 'area',
                            hover_data = ['population', 'medIncome'],
                            lat = 'latitude',
                            lon = 'longitude',
                            z = feature,
                            radius = 20,
                            center = center,
                            zoom = zoom,
                            height = 500,
                            color_continuous_scale = 'viridis',
                            labels = {feature : features_trans[feature]})
    fig.update_layout(mapbox_style="dark",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Now the feature bar chart

@app.callback(
    Output('bar_chart', 'figure'),
    [
    Input('state selection', 'value'),
    Input('feature selection', 'value')
    ]
)

def update_bar(state, feature):
    global feat_selected
    filtered_data = crime_data
    if state != 'All' and state is not None:
        filtered_data = crime_data[crime_data['state'] == state]
    if feature is None:
        feature = feat_selected
    else:
        feat_selected = feature
    
    # Prepare top 10
    # ready = filtered_data.groupby(feat_selected).sum()
    ready = filtered_data.sort_values(by = feat_selected, axis = 0, ascending = False)
    ready = ready.iloc[0:10,:]

    fig = px.bar(ready,
        x = 'area',
        y = feat_selected,
        hover_data=["state", "violent_crime_rate"],
        title = (f'Distribution of {features_trans[feature]} in {state}'),
        labels = {feat_selected : features_trans[feat_selected], 'area' : 'Area'}
    )
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    return fig

@app.callback(
    Output('corr_chart', 'figure'),
    [
    Input('state selection', 'value')
    ]
)

def update_corr(state):
    global feat_selected
    filtered_data = crime_data
    if state != 'All' and state is not None:
        filtered_data = crime_data[crime_data['state'] == state]
    
    filtered_data = filtered_data.drop(['latitude', 'longitude'], axis = 1)
    filtered_data = filtered_data.rename(columns = {'population' : 'Population', 'medIncome' : 'Median Income',
                                                     'PctPopUnderPov' : 'Percentage Population Under Poverty Line',
                                                     'PctUnemployed' : 'Percentage Population Unemployed',
                                                     'violent_crime_rate' : 'Violent Crime Rate'}, inplace= False)

    corr_matrix = filtered_data.corr()
    fig = ff.create_annotated_heatmap(
        x = list(corr_matrix.columns),
        y = list(corr_matrix.index),
        z = np.array(corr_matrix),
        annotation_text = np.around(np.array(corr_matrix), decimals=2),
        colorscale = 'Viridis'
    )


    return fig


if __name__ == '__main__':
    app.run_server(debug=True)