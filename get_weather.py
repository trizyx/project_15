import requests
from utils import detect_language


class WeatherAPI:
    def __init__(self, base_url: str, apikey: str) -> None:
        self.base_url = base_url
        self.apikey = apikey

    def get_location_weather(self, location: str):
        url = f"{self.base_url}locations/v1/cities/search"
        try:
            query = {
                'apikey': self.apikey,
                'q': location,
                'language': detect_language(location),
                'details': True,
                'toplevel': False,
            }
            response = requests.get(url=url, params=query)
            response.raise_for_status()
            location_data = response.json()
            if not location_data:
                raise ValueError(f"Нет результатов для локации: {location}")

            location_key = location_data[0]["Key"]
            return location_key

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            raise
        except (ValueError, IndexError) as e:
            print(f"Ошибка: {e}")
            raise

    def get_current_conditions(self, location_key: str):
        """Получение текущей погоды для локации."""
        url = f"{self.base_url}currentconditions/v1/{location_key}"
        try:
            query = {
                'apikey': self.apikey,
                'language': 'en-us',
                'details': True,
            }
            response = requests.get(url=url, params=query)
            response.raise_for_status()
            current_data = response.json()
            if not current_data:
                raise ValueError("Нет данных о текущей погоде.")

            weather = current_data[0]
            return {
                'temperature': weather.get('Temperature', {}).get('Metric', {}).get('Value', 'Нет данных'),
                'humidity': weather.get('RelativeHumidity', 'Нет данных'),
                'wind_speed': weather.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 'Нет данных'),
            }

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            raise
        except (ValueError, IndexError) as e:
            print(f"Ошибка: {e}")
            raise

    def get_weather_forecast(self, location_key: str, days: int = 1):
        """Получение прогноза погоды на 1, 3 или 5 дней."""
        if days not in [1, 3, 5]:
            raise ValueError("Доступны только прогнозы на 1, 3 или 5 дней.")
        url = f"{self.base_url}forecasts/v1/daily/{days}day/{location_key}"
        try:
            query = {
                'apikey': self.apikey,
                'language': 'en-us',
                'metric': True,
            }
            response = requests.get(url=url, params=query)
            response.raise_for_status()
            forecast_data = response.json()
            return forecast_data.get("DailyForecasts", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            raise
