from dash import Dash, dcc, html, Input, Output, callback_context, ALL, ctx
import dash_leaflet as dl
import plotly.graph_objs as go
import json
from ..utils.main import get_weather_data, get_city_coordinates
from app.utils.cities import cities


def init_dash(server):
    dash_app = Dash(__name__, server=server, url_base_pathname='/dash/')


    dash_app.layout = html.Div(
        [
            html.H1("Карта маршрута", style={"textAlign": "center"}),
            dl.Map(
                center=[55.751244, 37.618423],
                zoom=4,
                children=[
                    dl.TileLayer(),
                    dl.LayerGroup(id="markers-layer"),
                    dl.Polyline(id="route-line", positions=[]),
                ],
                id="map",
                style={"width": "100%", "height": "70vh"},
            ),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[
                    {"label": "Температура", "value": "temperature"},
                    {"label": "Скорость ветра", "value": "wind_speed"},
                    {"label": "Вероятность осадков", "value": "precipitation"},
                ],
                value="temperature",
                clearable=False,
                style={"width": "100%"},
            ),
            dcc.Dropdown(
                id="days-dropdown",
                options=[{"label": "3 дня", "value": 3}, {"label": "5 дней", "value": 5}],
                value=3,
                clearable=False,
                style={"width": "100%"},
            ),
            html.Div(id="weather-graph-container"),
        ]
    )


    @dash_app.callback(
        [Output("markers-layer", "children"), Output("route-line", "positions")],
        Input("map", "id"),
    )
    def add_route_and_markers(_):
        city_markers = []
        route_positions = []

        for city in cities:
            coords = get_city_coordinates(city)
            if coords:
                route_positions.append(coords)
                marker = dl.Marker(
                    position=coords,
                    children=[dl.Tooltip(city), dl.Popup([html.H3(city), html.P("")])],
                    id={"type": "marker", "index": city},
                )
                city_markers.append(marker)
        return city_markers, route_positions


    @dash_app.callback(
        Output("weather-graph-container", "children"),
        [Input("metric-dropdown", "value"), Input("days-dropdown", "value")],
        Input({"type": "marker", "index": ALL}, "n_clicks"),
    )
    def update_graph(selected_metric, days, _):

        city_name = cities[0]

        if (
            ctx.triggered_id
            and ctx.triggered_id != "metric-dropdown"
            and ctx.triggered_id != "days-dropdown"
        ):
            city_name = json.loads(callback_context.triggered[0]["prop_id"].split(".")[0])[
                "index"
            ]

        if city_name:
            weather_data = get_weather_data(city_name, days)
            if not weather_data is None:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=weather_data["date"],
                        y=weather_data[selected_metric],
                        mode="lines",
                        name=selected_metric,
                    )
                )
                fig.update_layout(
                    title=f"{selected_metric.capitalize()} в городе {city_name} за {days} дней",
                    xaxis_title="Дата",
                    yaxis_title="Значение",
                    template="plotly_dark",
                )
                return dcc.Graph(figure=fig)
        return html.Div("Выберите город для отображения графика")
