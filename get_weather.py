import requests
from utils import detect_language


class WeatherAPI:
    def __init__(self, base_url:str, apikey:str) -> None:
        self.base_url = base_url
        self.apikey = apikey

    def get_location_weather(self, location:str):
        url = f"{self.base_url}locations/v1/cities/search"
        try:
            query = {
            'apikey': self.apikey,
            'q': location,
            'language': detect_language(location),
            'details': True,
            'toplevel':False,

        }
            response = requests.get(url=url, params=query)
            response.raise_for_status()
            location_data = response.json()
            if not location_data:
                raise ValueError(f"Нет результатов для локации: {location}")

            location_key = location_data[0]["Key"]
            return location_key

        except requests.exceptions.RequestException as e:
            print(f"Плохой запрос {e}")
            raise
        except (ValueError, IndexError) as e:
            print(f"Ошибка {e}")
            raise


    def get_location_weather_coords(self, latitude:float, longitude:float):
        url = f"{self.base_url}locations/v1/cities/geoposition/search"
        try:
            query = {
            'apikey': self.apikey,
            'q': f'{latitude}, {longitude}',
            'language': 'en-us',
            'details': False,
            'toplevel':False,
        }
            response = requests.get(url=url, params=query)
            response.raise_for_status()
            location_data = response.json()
            if not location_data:
                raise ValueError(f"Нет результатов для локации: {latitude}, {longitude}")

            location_key = location_data[0]["Key"]
            return location_key

        except requests.exceptions.RequestException as e:
            print(f"Плохой запрос {e}")
            raise
        except (ValueError, IndexError) as e:
            print(f"Ошибка {e}")
            raise

        
    def get_weather(self, location_key: str):
        try:
            request_url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}'
            query = {
                'apikey': self.apikey,
                'language': 'en-us',
                'details': True,
                'metric': True,
            }
            response = requests.get(url=request_url, params=query)

            if response.status_code == 200:
                weather = response.json()[0]  # Get the first hour's weather data
                temperature = weather.get('Temperature', {}).get('Value')
                humidity = weather.get('RelativeHumidity')
                wind = weather.get('Wind', {})
                wind_speed = wind.get('Speed', {}).get('Value')
                # print(weather) дебажил)

                if temperature is None or humidity is None or wind_speed is None:
                    raise ValueError("Бед запрос реквест нету данных.")

                return {
                    'temperature': temperature,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                }

            raise Exception(f"Ерор фетчинг дата: {response.status_code} | {response.text}")

        except Exception as e:
            print(f"Error in get_weather: {e}")
            return None
        
    def get_weather_forecast(self, location_key, days=1):
        """
        Получение прогноза погоды на несколько дней.
        """
        if days not in [1, 3, 5]:
            raise ValueError("Доступны только прогнозы на 1, 3 или 5 дней.")
        endpoint = f"forecasts/v1/daily/{days}day/{location_key}"
        params = {"apikey": self.apikey, "language": "en-us", "metric": True}
        response = requests.get(self.base_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()

