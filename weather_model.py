class WeatherModel:
    def check_bad_weather(self,
                          temperature: int,
                          windspeed:int,
                          humidity:int) -> str:
        if temperature and windspeed and humidity:
            if temperature < 0:
                return "Плохие погодные условия: мороз"
        
            elif temperature > 30:
                return "Плохие погодные условия: жара"
            
            elif windspeed > 20:
                return "Плохие погодные условия: сильный ветер"
            
            elif humidity > 80:
                return "Плохие погодные условия: высокая влажность"
            
            return "Хорошие погодные условия"

        else:
            return "Некорректные погодные данные"

