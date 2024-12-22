from flask import Flask, render_template, request
from dash import Dash, dcc, html
import plotly.graph_objects as go
from get_weather import WeatherAPI
from weather_model import WeatherModel

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')
weather_api = WeatherAPI(base_url="http://dataservice.accuweather.com/", apikey='IYTqLFyPye5LKcAoFUjPwfh9oOg25YT9')
weather_model = WeatherModel()

@app.route("/", methods=["GET", "POST"])
def index():
    forecast_data = []
    error_message = None
    graph_url = None

    if request.method == "POST":
        search_type = request.form.get("search_type")
        points = request.form.get("points")

        # Проверяем, что введены точки маршрута
        if points:
            points = points.split(',')  # Разделяем по запятой
        else:
            points = []

        try:
            for point in points:
                point = point.strip()  # Убираем лишние пробелы
                print(f"Ищу погоду для города: {point}")  # Логируем запрос

                # Получаем ключ локации
                location_key = weather_api.get_location_weather(point)
                print(f"Ключ локации для {point}: {location_key}")  # Логируем ключ

                if location_key:
                    weather_data = weather_api.get_weather(location_key)
                    print(f"Полученные данные погоды для {point}: {weather_data}")  # Логируем данные

                    if weather_data:
                        temperature = weather_data.get('temperature', 'Нет данных')
                        humidity = weather_data.get('humidity', 'Нет данных')
                        wind_speed = weather_data.get('wind_speed', 'Нет данных')

                        forecast_data.append({
                            'point': point,
                            'temperature': temperature,
                            'humidity': humidity,
                            'wind_speed': wind_speed
                        })
                    else:
                        forecast_data.append({
                            'point': point,
                            'temperature': 'Нет данных',
                            'humidity': 'Нет данных',
                            'wind_speed': 'Нет данных'
                        })
                else:
                    forecast_data.append({
                        'point': point,
                        'temperature': 'Нет данных',
                        'humidity': 'Нет данных',
                        'wind_speed': 'Нет данных'
                    })

            # If data is available, setup Dash graph
            if forecast_data:
                setup_dash(forecast_data)
                graph_url = "/dash/"

        except Exception as e:
            error_message = f"Ошибка при получении данных: {e}"

    return render_template("index.html", forecast_data=forecast_data, error_message=error_message, graph_url=graph_url)


def setup_dash(forecast_data):
    """Configure Dash app with weather data."""
    fig = go.Figure()

    # Графики для каждого города
    for data in forecast_data:
        # Температура
        fig.add_trace(go.Scatter(
            x=["Now"], y=[data['temperature']],
            mode="lines+markers", name=f"Температура ({data['point']})"
        ))
        # Влажность
        fig.add_trace(go.Scatter(
            x=["Now"], y=[data['humidity']],
            mode="lines+markers", name=f"Влажность ({data['point']})"
        ))
        # Скорость ветра
        fig.add_trace(go.Scatter(
            x=["Now"], y=[data['wind_speed']],
            mode="lines+markers", name=f"Скорость ветра ({data['point']})"
        ))

    fig.update_layout(
        title="Прогноз погоды для точек маршрута",
        xaxis_title="Время",
        yaxis_title="Значение",
        template="plotly_white",
        height=600
    )

    dash_app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])


if __name__ == "__main__":
    app.run(debug=True)
