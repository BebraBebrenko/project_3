from flask import Flask, render_template, request, redirect
from dash import Dash, dcc, html, Input, Output, callback_context, ALL, ctx
import dash_leaflet as dl
import plotly.graph_objs as go
import json
import pandas as pd
from .utils.main import get_weather_data, get_city_coordinates

app = Flask(__name__)

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

cities = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global cities
    if request.method == 'POST':
        start_point = request.form['start_point']
        end_point = request.form['end_point']
        intermediate_cities = request.form.getlist('intermediate_city')

        cities = [start_point, end_point] + intermediate_cities
        return redirect('/dash/')
    
    return render_template('index.html')

dash_app.layout = html.Div([
    html.H1("Карта маршрута"),

    # Flex container for map and weather graph
    html.Div([
        # Map element
        dl.Map(center=[50, 50], zoom=4, children=[
            dl.TileLayer(),
            dl.LayerGroup(id="markers-layer"),
            dl.Polyline(id="route-line", positions=[])
        ], id="map", style={'width': '50vw', 'height': '50vh'}),
        
        # Weather graph container
        html.Div(id='weather-graph-container', style={'width': '50vw', 'height': '50vh'})
    ], style={'display': 'flex', 'width': '100%', 'justify-content': 'space-between'}),

    # Dropdowns below the map and graph
    html.Div([
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Температура', 'value': 'temperature'},
                {'label': 'Скорость ветра', 'value': 'wind_speed'},
                {'label': 'Вероятность осадков', 'value': 'precipitation'}
            ],
            value='temperature',
            clearable=False,
            style={'width': '50%'}
        ),
        
        dcc.Dropdown(
            id='days-dropdown',
            options=[
                {'label': '3 дня', 'value': 3},
                {'label': '5 дней', 'value': 5}
            ],
            value=3,
            clearable=False,
            style={'width': '50%'}
        )
    ], style={'width': '100%', 'marginTop': '10px', 'display': 'flex', 'justify-content': 'center'})
])

@dash_app.callback(
    [Output("markers-layer", "children"), Output("route-line", "positions")],
    Input('map', 'id')
)
def add_route_and_markers(_):
    city_markers = []
    route_positions = []
    
    for city in cities:
        coords = get_city_coordinates(city)
        if coords:
            route_positions.append(coords)
            marker = dl.Marker(position=coords, children=[
                dl.Tooltip(city),
                dl.Popup([html.H3(city), html.P("Нажмите для данных")])
            ], id={'type': 'marker', 'index': city})
            city_markers.append(marker)
    return city_markers, route_positions

@dash_app.callback(
    Output("weather-graph-container", "children"),
    [Input("metric-dropdown", "value"), Input("days-dropdown", "value")],
    Input({'type': 'marker', 'index': ALL}, 'n_clicks')
)
def update_graph(selected_metric, days, _):
    triggered = callback_context.triggered[0]['value']
    print(ctx.triggered_id)

    city_name = cities[0] if len(cities) > 0 else None
    def replace_value(input_str):
        mapping = {
            'temperature': 'Температура',
            'wind_speed': 'Скорость ветра',
            'precipitation': 'Вероятность осадков'
        }
        return mapping.get(input_str, input_str)

    if ctx.triggered_id and ctx.triggered_id != "metric-dropdown" and ctx.triggered_id != "days-dropdown":
        city_name = json.loads(callback_context.triggered[0]['prop_id'].split(".")[0])["index"]

    if city_name:
        weather_data = get_weather_data(city_name, days) 
        if not weather_data is None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=weather_data['date'], y=weather_data[selected_metric], mode='lines', name=selected_metric))
            fig.update_layout(
                title=f'{replace_value(selected_metric)} в городе {city_name} за {days} дней',
                xaxis_title='Дата',
                yaxis_title='Значение',
                template='plotly_white'
            )
            return dcc.Graph(figure=fig)
    return html.Div("Выберите город для отображения графика")
