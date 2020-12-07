import dash
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
from f_model import *


def labeling(x, values):
    if x == values['max']:
        return 'red'
    if x == values['mid']:
        return 'orange'
    if x == values['min']:
        return 'green'


def max_min_mid(affected_0, affected_1, affected_2):
    if affected_0 > affected_1 > affected_2:
        return dict(max=0, mid=1, min=2)
    if affected_0 > affected_2 > affected_1:
        return dict(max=0, mid=2, min=1)
    if affected_1 > affected_0 > affected_2:
        return dict(max=1, mid=0, min=2)
    if affected_1 > affected_2 > affected_0:
        return dict(max=1, mid=2, min=0)
    if affected_2 > affected_1 > affected_0:
        return dict(max=2, mid=1, min=0)
    if affected_2 > affected_0 > affected_1:
        return dict(max=2, mid=0, min=1)


def labels_based_effect(df, column):
    df_aux = pd.DataFrame()
    df_aux['0'] = np.where(df['labels'] == 0, column, 0)
    affected_0 = df_aux['0'].max()

    df_aux['1'] = np.where(df['labels'] == 1, column, 0)
    affected_1 = df_aux['1'].max()

    df_aux['2'] = np.where(df['labels'] == 2, column, 0)
    affected_2 = df_aux['2'].max()
    print("a0" + affected_0.astype(str))
    print("a1" + affected_1.astype(str))
    print("a2" + affected_2.astype(str))
    return max_min_mid(affected_0, affected_1, affected_2)


def plotly_map_impact(year, hazard):
    df = wildfires_data()
    natural_hazard = "Wildfires"
    clustering = wildfires_clustering()

    # I put in a new dataframe the species and the labels so I can figure out which label has each specie
    df['labels'] = clustering['labels']

    values = labels_based_effect(df, df['SIZE_HA'])
    df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

    df = df[(df['YEAR'] == year)]  # I get the year I want
    size_points = df['SIZE_HA']/100
    latitude = df['LATITUDE']
    longitude = df['LONGITUDE']
    text = "date:" + df['YEAR'].astype(str) + "-" + df['MONTH'].astype(str) + " - HA affected:" + df['SIZE_HA'].astype(str) + " - Province: " + df['SRC_AGENCY'].astype(str)

    if hazard == "Earthquakes":
        df = earthquakes_data()
        natural_hazard = "Earthquakes"
        clustering = earthquakes_clustering()
        df['labels'] = clustering['labels']

        values = labels_based_effect(df, df['depth'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        size_points = df['depth']
        latitude = df['latitude']
        longitude = df['longitude']
        text = "date:" + df['date'] + "- depth:" + df['depth'].astype(str) + "- magnitude:" + df['magnitude'].astype(str) + "- place:" + df['place'].astype(str)
    if hazard == "Tornadoes":
        df = tornadoes_data()
        natural_hazard = "Tornadoes"
        clustering = tornadoes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FUJITA'].astype(int) + df['HUMAN_FATAL'].astype(int) + df['HUMAN_INJ']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YYYY_LOCAL'] == year)]  # I get the year I want

        size_points = df['FUJITA'].astype(int) + df['HUMAN_FATAL'].astype(int) + df['HUMAN_INJ'].astype(int)
        latitude = df['START_LAT_N']
        longitude = df['START_LON_W']
        text = "date" + df['YYYY_LOCAL'].astype(str) + " - " + df['MM_LOCAL'].astype(str) + " - Place: "+df['NEAR_CMMTY'].astype(str)
    if hazard == "Floods":
        df = floods_data()
        natural_hazard = "Floods"
        clustering = floods_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])

        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        size_points = df['effect']
        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + "- injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)
    if hazard == "Hurricanes":
        df = hurricanes_data()
        natural_hazard = "Hurricanes"
        clustering = hurricanes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        size_points = df['effect']
        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + "- injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=longitude,
        lat=latitude,
        text=text,
        marker=dict(
            color=df['colors'],
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode='area'
        )
    ))

    fig.update_layout(
        autosize=True,
        mapbox=dict(pitch=0),
        title_text=natural_hazard,
        showlegend=True,
        paper_bgcolor='#4E5D6C',
        plot_bgcolor='#4E5D6C',
        font=dict(color="#2cfec1"),
        geo=dict(
            scope='north america',
            landcolor='rgb(217, 217, 217)',
            bgcolor='rgba(0,0,0,0)'
        )
    )

    return fig


def plotly_relieve(year, hazard):
    df = wildfires_data()
    clustering = wildfires_clustering()

    # I put in a new dataframe the species and the labels so I can figure out which label has each specie
    df['labels'] = clustering['labels']

    values = labels_based_effect(df, df['SIZE_HA'])
    df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

    df = df[(df['YEAR'] == year)]  # I get the year I want

    latitude = df['LATITUDE']
    longitude = df['LONGITUDE']
    text = "date:" + df['YEAR'].astype(str) + "-" + df['MONTH'].astype(str) + " - HA affected:" + df['SIZE_HA'].astype(str) + " - Province: " + df['SRC_AGENCY'].astype(str)

    if hazard == "Tornadoes":
        df = tornadoes_data()
        clustering = tornadoes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FUJITA'].astype(int) + df['HUMAN_FATAL'].astype(int) + df['HUMAN_INJ']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YYYY_LOCAL'] == year)]  # I get the year I want

        latitude = df['START_LAT_N']
        longitude = df['START_LON_W']
        text = "date" + df['YYYY_LOCAL'].astype(str) + " - " + df['MM_LOCAL'].astype(str) + " - Place: "+df['NEAR_CMMTY'].astype(str)
    if hazard == "Earthquakes":
        df = earthquakes_data()
        clustering = earthquakes_clustering()

        df['labels'] = clustering['labels']
        values = labels_based_effect(df, df['depth'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['latitude']
        longitude = df['longitude']
        text = "date:" + df['date'] + "- depth:" + df['depth'].astype(str) + "- magnitude:" + df['magnitude'].astype(str) + "- place:" + df['place'].astype(str)
    if hazard == "Floods":
        df = floods_data()
        clustering = floods_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + "- injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)
    if hazard == "Hurricanes":
        df = hurricanes_data()
        clustering = hurricanes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + "- injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)

    fig = px.scatter_mapbox(df,
                            lat=latitude,
                            lon=longitude,
                            hover_name=text,
                            color='colors',
                            zoom=3)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            },
            {
                "sourcetype": "raster",
                "sourceattribution": "Government of Canada",
                "source": ["https://geo.weather.gc.ca/geomet/?"
                           "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
                           "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
            }
        ])
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig


def plotly_states(year, hazard):
    df = wildfires_data()
    clustering = wildfires_clustering()

    # I put in a new dataframe the species and the labels so I can figure out which label has each specie
    df['labels'] = clustering['labels']

    values = labels_based_effect(df, df['SIZE_HA'])

    df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
    df = df[(df['YEAR'] == year)]  # I get the year I want

    latitude = df['LATITUDE']
    longitude = df['LONGITUDE']
    text = "date:" + df['YEAR'].astype(str) + "-" + df['MONTH'].astype(str) + " - HA affected:" + df['SIZE_HA'].astype(str) + " - Province: " + df['SRC_AGENCY'].astype(str)

    if hazard == "Tornadoes":
        df = tornadoes_data()
        clustering = tornadoes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FUJITA'].astype(int) + df['HUMAN_FATAL'].astype(int) + df['HUMAN_INJ']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YYYY_LOCAL'] == year)]  # I get the year I want

        latitude = df['START_LAT_N']
        longitude = df['START_LON_W']
        text = "date" + df['YYYY_LOCAL'].astype(str) + " - " + df['MM_LOCAL'].astype(str) + " - Place: "+df['NEAR_CMMTY'].astype(str)
    if hazard == "Earthquakes":
        df = earthquakes_data()
        clustering = earthquakes_clustering()

        df['labels'] = clustering['labels']
        values = labels_based_effect(df, df['depth'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['latitude']
        longitude = df['longitude']
        text = "date:" + df['date'] + "- depth:" + df['depth'].astype(str) + "- magnitude:" + df['magnitude'].astype(str) + "- place:" + df['place'].astype(str)
    if hazard == "Floods":
        df = floods_data()
        clustering = floods_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + " - injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)
    if hazard == "Hurricanes":
        df = hurricanes_data()
        clustering = hurricanes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + "- injured & fatalities & evacuated:" + df['effect'].astype(str) + " - place:" + df['PLACE'].astype(str)

    fig = px.scatter_mapbox(df,
                            lat=latitude,
                            lon=longitude,
                            hover_name=text,
                            color='colors',
                            zoom=3)
    fig.update_layout(
        mapbox_style="open-street-map"
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def weather(year, chart, province):
    if province == "Saskatchewan":
        weather = pd.read_csv('sk_weather.csv', sep=",")
    if province == "Nova Scotia":
        weather = pd.read_csv('ns_weather.csv', sep=",")
    if province == "Ontario":
        weather = pd.read_csv('ontario_weather.csv', sep=",")
    if province == "Newfoundland and Labrador":
        weather = pd.read_csv('nl_weather.csv', sep=",")
    if province == "Quebec":
        weather = pd.read_csv('qc_weather.csv', sep=",")
    if province == "Alberta":
        weather = pd.read_csv('al_weather.csv', sep=",")
    if province == "British Columbia":
        weather = pd.read_csv('bc_weather.csv', sep=",")
    if province == "Manitoba":
        weather = pd.read_csv('mb_weather.csv', sep=",")
    if province == "New Brunswick":
        weather = pd.read_csv('nb_weather2.csv', sep=",")
    if province == "Nunavut":
        weather = pd.read_csv('nu_weather.csv', sep=",")
    if province == "Northwestern Territories":
        weather = pd.read_csv('nw_weather.csv', sep=",")
    if province == "Prince Edward Island":
        weather = pd.read_csv('prince_weather.csv', sep=",")
    if province == "Yukon":
        weather = pd.read_csv('yk_weather.csv', sep=",")

    weather = fix_nans(weather, 'Total Rain (mm)')
    weather = fix_nans(weather, 'Total Precip (mm)')
    weather = fix_nans(weather, 'Mean Max Temp (°C)')
    weather = fix_nans(weather, 'Mean Min Temp (°C)')
    weather = fix_nans(weather, 'Mean Temp (°C)')

    weather = weather[(weather['Year'] == year)]
    if chart == "Bar":
        fig = px.bar(weather, x='Month', y='Total Rain (mm)', title= 'Rain (mm) in ' + province + ' ' + str(year))
        fig.update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font=dict(color="#2cfec1"))
        fig.update_traces(marker_color='#2cfec1')
        return fig
    if chart == "Line":
        fig = px.line(weather, x="Month", y=["Mean Min Temp (°C)", "Mean Max Temp (°C)", "Mean Temp (°C)"], title='Temperatures (C°) in ' + province + ' ' + str(year))
        fig.update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font=dict(color="#2cfec1"),
        )
        fig.update_traces(marker_color='#2cfec1')
        return fig
    if chart == "Scatter":
        fig = px.scatter(weather, x="Month", y="Total Snow (cm)", marginal_y="violin",
                         marginal_x="box", trendline="ols", template="simple_white", title='Snow (mm)  in ' + province + ' ' + str(year))
        fig.update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font=dict(color="#2cfec1"),
        )
        fig.update_traces(marker_color='#2cfec1')
        return fig
    if chart == "Histogram":
        fig = px.histogram(weather, x="Month", y="Total Precip (mm)", title='Total Precip (mm) in ' + province + ' ' + str(year), nbins=4)
        fig.update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font=dict(color="#2cfec1"),
        )
        fig.update_traces(marker_color='#2cfec1')
        return fig


def table_figure(year, hazard):
    df = wildfires_data()

    df = wildfires_data()
    clustering = wildfires_clustering()

    # I put in a new dataframe the species and the labels so I can figure out which label has each specie
    df['labels'] = clustering['labels']

    values = labels_based_effect(df, df['SIZE_HA'])

    df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
    df = df[(df['YEAR'] == year)]  # I get the year I want

    latitude = df['LATITUDE']
    longitude = df['LONGITUDE']
    text = "date:" + df['YEAR'].astype(str) + "-" + df['MONTH'].astype(str) + "HA affected:" + df['SIZE_HA'].astype(str)

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(['Year', 'Month', 'Latitude', 'Longitude', 'Area affected (HA)', 'Cause']),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df['YEAR'], df['MONTH'], latitude, longitude, df['SIZE_HA'], df['CAUSE']],
                   fill_color='lavender',
                   align='left'))
    ])

    if hazard == "Tornadoes":
        df = tornadoes_data()
        clustering = tornadoes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FUJITA'].astype(int) + df['HUMAN_FATAL'].astype(int) + df['HUMAN_INJ']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YYYY_LOCAL'] == year)]  # I get the year I want

        latitude = df['START_LAT_N']
        longitude = df['START_LON_W']
        text = df['YYYY_LOCAL'].astype(str) + "-" + df['MM_LOCAL'].astype(str)

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(['Year', 'Month', 'Latitude', 'Longitude', 'Place', 'Magnitude', 'Fatalities', 'Injuries']),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df['YYYY_LOCAL'], df['MM_LOCAL'], latitude, longitude, df['NEAR_CMMTY'], df['FUJITA'], df['HUMAN_FATAL'], df['HUMAN_INJ']],
                       fill_color='lavender',
                       align='left'))
        ])
    if hazard == "Earthquakes":
        df = earthquakes_data()
        clustering = earthquakes_clustering()

        df['labels'] = clustering['labels']
        values = labels_based_effect(df, df['depth'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['latitude']
        longitude = df['longitude']
        text = "date:" + df['date'] + "depth:" + df['depth'].astype(str) + "magnitude:" + df['magnitude'].astype(
            str) + "place:" + df['place'].astype(str)

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(['Date', 'Latitude', 'Longitude', 'Magnitude', 'Magnitude type', 'Depth']),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df['date'], latitude, longitude,  df['magnitude'],  df['magnitude type'],  df['depth']],
                       fill_color='lavender',
                       align='left'))
        ])
    if hazard == "Floods":
        df = floods_data()
        clustering = floods_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))
        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + " injured & fatalities & evacuated:" + df['effect'].astype(str)

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(['Event', 'Latitude', 'Longitude', 'Place', 'Magnitude', 'Fatalities', 'Injuries', 'Evacuations']),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df['EVENT'], latitude, longitude, df['PLACE'], df['MAGNITUDE'], df['FATALITIES'], df['INJURED / INFECTED'], df['EVACUATED']],
                       fill_color='lavender',
                       align='left'))
        ])
    if hazard == "Hurricanes":
        df = hurricanes_data()
        clustering = hurricanes_clustering()

        df['labels'] = clustering['labels']
        df['effect'] = df['FATALITIES'] + df['INJURED / INFECTED'] + df['EVACUATED']
        values = labels_based_effect(df, df['effect'])
        df['colors'] = df['labels'].apply(lambda x: labeling(x, values))

        df = df[(df['YEAR'] == year)]  # I get the year I want

        latitude = df['LATITUDE']
        longitude = df['LONGITUDE']
        text = "date: " + df['EVENT'].astype(str) + " injured & fatalities & evacuated:" + df['effect'].astype(str)

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(
                ['Event', 'Latitude', 'Longitude', 'Place', 'Magnitude', 'Fatalities', 'Injuries', 'Evacuations']),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df['EVENT'], latitude, longitude, df['PLACE'], df['MAGNITUDE'], df['FATALITIES'],
                               df['INJURED / INFECTED'], df['EVACUATED']],
                       fill_color='lavender',
                       align='left'))
        ])

    fig.update_layout(
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        title_text=hazard + " in Canada in " + str(year)
    )
    return fig


def dash_task():
    app = dash.Dash(
        __name__,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
        ],
    )
    server = app.server
    df1_aux = wildfires_data()
    df1 = df1_aux['YEAR'].unique()
    df1 = np.sort(df1)
    df2_aux = earthquakes_data()
    df2 = df2_aux['YEAR'].unique()
    df2 = np.sort(df2)
    df3_aux = tornadoes_data()
    df3 = df3_aux['YYYY_LOCAL'].unique()
    df3 = np.sort(df3)
    df5_aux = hurricanes_data()
    df5 = df5_aux['YEAR'].unique()
    df5 = np.sort(df5)
    df4_aux = floods_data()
    df4 = df4_aux['YEAR'].unique()
    df4 = np.sort(df4)

    options_list = {
        'Wildfires': df1,
        'Earthquakes': df2,
        'Tornadoes': df3,
        'Floods': df4,
        'Hurricanes': df5
    }

    app.layout = html.Div(
        id="root",
        children=[
            html.Div(
                id="header",
                children=[
                    html.H4(children="Visualizing Canadian Natural Hazards"),
                    html.P(
                        id="description",
                        children="Natural hazards are identified with three (3) different colors in maps: "
                                 "Red represents the ones with highest impact, "
                                 "Orange represents the ones with mid impact and Green the ones with the lowest impact."
                                 "Even though in nature map and province map the color of dots differ from legends, the valid information are legends"),
                ],
            ),
            html.Div(
                id="app-container",
                children=[
                    html.Div(
                        id="left-column",
                        children=[
                            html.Div(
                                id="slider-container",
                                children=[
                                    html.P(
                                        id="dropdown-text",
                                        children="Natural hazard:",
                                        style=dict(width='10%')
                                    ),
                                    dcc.Dropdown(
                                        options=[{'label': k, 'value': k} for k in options_list.keys()],
                                        value="Tornadoes",
                                        id="dropdown-hazard",
                                        style=dict(width='40%')
                                    ),
                                    html.P(
                                        id="slider-text",
                                        children="Year:",
                                        style=dict(width='10%')
                                    ),
                                    dcc.Dropdown(
                                        id="dropdown-y",
                                        style=dict(width='22%')
                                    ),
                                    html.P(
                                        id="map-text",
                                        children="Type of map:",
                                        style = dict(width='16%')
                                    ),
                                    dcc.RadioItems(
                                        id='radio-button',
                                        options=[
                                            {'label': 'Bubble map ', 'value': 'Bubble'},
                                            {'label': 'Nature map ', 'value': 'Relieve'},
                                            {'label': 'Province map ', 'value': 'States'},
                                        ],
                                        value='Bubble',
                                        style=dict(width='16%')
                                    )
                                ], style=dict(display='flex')
                            ),
                            html.Div(
                                id="heatmap-container",
                                children=[
                                    dcc.Graph(id='example-graph')
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        id="graph-container",
                        children=[
                            html.P(id="chart-selector", children="Select chart:"),
                            dcc.Dropdown(
                                id="chart-dropdown",
                                value="Bar",
                                options=[
                                    {
                                        "label": "Bar chart of rain in province of selected city",
                                        "value": "Bar"
                                    },
                                    {
                                        "label": "Histogram of precipitations in province of selected city",
                                        "value": "Histogram"
                                    },
                                    {
                                        "label": "Line chart of temperatures in province of selected city",
                                        "value": "Line"
                                    },
                                    {
                                        "label": "Scatter plot of snow in province of selected city",
                                        "value": "Scatter"
                                    },
                                ]
                            ),
                            dcc.Graph(
                                id="example-prediction"
                            ),
                        ],
                    ),
               ],
            ),
            html.Div(
                id="table-container",
                children=[
                    dcc.Graph(
                        id="table-prediction"
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output('dropdown-y', 'options'),
        [Input('dropdown-hazard', 'value')])
    def set_options(selected_df):
        return [{'label': i, 'value': i} for i in options_list[selected_df]]

    @app.callback(
        Output('dropdown-y', 'value'),
        [(Input('dropdown-y', 'options'))])
    def set_y_value(selected_df):
        return selected_df[0]['value']

    @app.callback(
        Output('table-prediction', 'figure'),
        [Input('dropdown-y', 'value'),
         Input('dropdown-hazard', 'value')])
    def table_data(year, hazard):
        return table_figure(year, hazard)

    @app.callback(
        Output('example-graph', 'figure'),
        [Input('dropdown-y', 'value'),
         Input('dropdown-hazard', 'value'),
         Input('radio-button', 'value')])
    def update_figure(year, hazard, radio):
        if radio == 'Bubble':
            return plotly_map_impact(year, hazard)
        if radio == 'Relieve':
            return plotly_relieve(year, hazard)
        if radio == 'States':
            return plotly_states(year, hazard)

    @app.callback(
        Output('example-prediction', 'figure'),
        [Input('dropdown-y', 'value'),
         Input('chart-dropdown', 'value'),
         Input('example-graph', 'clickData')])
    def update_figure_prediction(year, chart, clickData):
        print(clickData)
        if clickData is None:
            return dict(
                data=[dict(x=0, y=0)],
                layout=dict(
                    title="Click on the map to select provinces",
                    paper_bgcolor="#1f2630",
                    plot_bgcolor="#1f2630",
                    font=dict(color="#2cfec1"),
                    margin=dict(t=75, r=50, b=100, l=75),
                ),
            )

        pts = clickData["points"]
        # Depending on latitude and longitude, I select the province
        if 47.03 >= int(pts[0]['lat']) >= 43.42 and -59.68 >= int(pts[0]['lon']) >= -66.32:
            return weather(year, chart, "Nova Scotia")
        if 60.00 >= int(pts[0]['lat']) >= 48.99 and -101.36 >= int(pts[0]['lon']) >= -109.99:
            return weather(year, chart, "Saskatchewan")
        if 62.59 >= int(pts[0]['lat']) >= 44.99 and -57.10 >= int(pts[0]['lon']) >= -79.76:
            return weather(year, chart, "Quebec")
        if 56.86 >= int(pts[0]['lat']) >= 41.66 and -74.34 >= int(pts[0]['lon']) >= -95.16:
            return weather(year, chart, "Ontario")
        if (60.37 >= int(pts[0]['lat']) >= 46.61 and -52.61 >= int(pts[0]['lon']) >= -67.80) or (47.80 >= int(pts[0]['lat']) >= 47.18 and -60.13 >= int(pts[0]['lon']) >= -61.50):
            return weather(year, chart, "Newfoundland and Labrador")
        if 60.00 >= int(pts[0]['lat']) >= 48.99 and -109.99 >= int(pts[0]['lon']) >= -120.00:
            return weather(year, chart, "Alberta")
        if 69.65 >= int(pts[0]['lat']) >= 60.00 and -123.81 >= int(pts[0]['lon']) >= -141.00:
            return weather(year, chart, "Yukon")
        if 60.00 >= int(pts[0]['lat']) >= 48.30 and -114.03 >= int(pts[0]['lon']) >= -139.06:
            return weather(year, chart, "British Columbia")
        if 83.11 >= int(pts[0]['lat']) >= 51.64 and -61.08 >= int(pts[0]['lon']) >= -120.68:
            return weather(year, chart, "Nunavut")
        if 60.00 >= int(pts[0]['lat']) >= 48.99 and -88.94 >= int(pts[0]['lon']) >= -102.03:
            return weather(year, chart, "Manitoba")
        if 78.76 >= int(pts[0]['lat']) >= 60.00 and -101.98 >= int(pts[0]['lon']) >= -136.44:
            return weather(year, chart, "Northwestern Territories")
        if 47.06 >= int(pts[0]['lat']) >= 45.95 and -61.97 >= int(pts[0]['lon']) >= -64.41:
            return weather(year, chart, "Prince Edward Island")
        if 48.07 >= int(pts[0]['lat']) >= 44.60 and -63.77 >= int(pts[0]['lon']) >= -69.06:
            return weather(year, chart, "New Brunswick")

    return app


if __name__ == "__main__":
    app_t = dash_task()
    app_t.run_server(debug=True)
