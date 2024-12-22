from flask import Flask, render_template, request
from get_weather import WeatherAPI
from dash import Dash, dcc, html
from weather_model import WeatherModel
import plotly.graph_objects as go

weather_model = WeatherModel()
app = Flask(__name__)
dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/',
)

weather_api = WeatherAPI(base_url="http://dataservice.accuweather.com/", apikey="GWAEh1lRGchlfBTZOuMtN2neGV5GfDoP")


def setup_dash(forecast_data, interval):
    """Настройка Dash с данными погоды."""
    fig = go.Figure()
    if forecast_data:
        for data in forecast_data:
            if data.get('data'):
                dates = [day['date'] for day in data['data']]
                temperatures = [day['temperature'] for day in data['data']]
                humidities = [day.get('humidity', 'Нет данных') for day in data['data']]
                wind_speeds = [day.get('wind_speed', 'Нет данных') for day in data['data']]

                fig.add_trace(go.Scatter(
                    x=dates, y=temperatures,
                    mode="lines+markers", name=f"Температура ({data['point']})"
                ))
                fig.add_trace(go.Scatter(
                    x=dates, y=humidities,
                    mode="lines+markers", name=f"Влажность ({data['point']})"
                ))
                fig.add_trace(go.Scatter(
                    x=dates, y=wind_speeds,
                    mode="lines+markers", name=f"Скорость ветра ({data['point']})"
                ))

    fig.update_layout(
        title=f"Прогноз погоды на {interval} дней",
        xaxis_title="Дата",
        yaxis_title="Значение",
        template="plotly_white",
        height=600
    )

    dash_app.layout = html.Div([
        dcc.Graph(figure=fig),
        html.Div([
            html.Label("Выберите временной интервал:"),
            dcc.Dropdown(
                id='interval-dropdown',
                options=[
                    {'label': '1 день', 'value': '1'},
                    {'label': '3 дня', 'value': '3'},
                    {'label': '5 дней', 'value': '5'}
                ],
                value=interval,
                clearable=False
            )
        ])
    ])


@app.route("/", methods=["GET", "POST"])
def index():
    forecast_data = []
    error_message = None
    graph_url = "/dash/"
    interval = request.form.get("interval", "1")

    if request.method == "POST":
        cities = request.form.get("cities")
        if not cities:
            error_message = "Пожалуйста, введите хотя бы один город."
        else:
            cities_list = [city.strip() for city in cities.split(",")]
            for city in cities_list:
                try:
                    location_key = weather_api.get_location_weather(city)
                    forecast = weather_api.get_weather_forecast(location_key, days=int(interval))
                    current_conditions = weather_api.get_current_conditions(location_key)

                    city_data = {
                        "point": city,
                        "data": [
                            {
                                "date": day["Date"],
                                "temperature": day["Temperature"]["Maximum"]["Value"],
                                "humidity": current_conditions.get('humidity', 'Нет данных'),
                                "wind_speed": current_conditions.get('wind_speed', 'Нет данных'),
                                "analysis": weather_model.check_bad_weather(
                                    temperature=day["Temperature"]["Maximum"]["Value"],
                                    windspeed=current_conditions.get('wind_speed', None),
                                    humidity=current_conditions.get('humidity', None),
                                ),
                            } for day in forecast
                        ]
                    }
                    forecast_data.append(city_data)
                except Exception as e:
                    error_message = f"Ошибка при получении данных: {e}"

    setup_dash(forecast_data, interval)
    return render_template("index.html", forecast_data=forecast_data, error_message=error_message, graph_url=graph_url, interval=interval)


if __name__ == "__main__":
    app.run(debug=True)
