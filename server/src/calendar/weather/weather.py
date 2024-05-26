import python_weather
from python_weather.forecast import HourlyForecast
from datetime import datetime

import parsedatetime
cal = parsedatetime.Calendar()

def parse_date(x):
    return cal.parseDT(datetimeString=x)[0].date() if len(cal.parseDT(datetimeString=x))>=2 else None

def parse_datetime(x):
    return cal.parseDT(datetimeString=x)[0] if len(cal.parseDT(datetimeString=x))>=2 else None
def str_date(x):
    return x.strftime("%Y-%m-%d")
def str_datetime(x):
    return x.strftime("%Y-%m-%d %H:%M:%S")

def str_time(x):
    return x.strftime("%H:%M")

class Forecast:

    def __init__(self,temperature,date,kind,description,emoji,adverse_weather=None):
        self.temperature = temperature
        self.date = date
        self.kind = kind
        self.description = description
        self.emoji = emoji
        self.adverse_weather = adverse_weather
        self.hourly_forecasts = []

    def get_temperature(self)->int:
        return self.temperature
    def get_date(self) -> datetime:
        return self.date
    def get_kind(self):
        return self.kind
    def get_description(self):
        return self.description
    def get_emoji(self):
        return self.emoji
    def get_adverse_weather(self):
        return self.adverse_weather
    def set_hourly_forecasts(self,hourly_forecasts):
        self.hourly_forecasts = hourly_forecasts
        return self
    def get_hourly_forecasts(self):
        return self.hourly_forecasts
    def __repr__(self):
        return f"{self.temperature} {self.date} {self.kind} {self.description} {self.emoji} {self.adverse_weather} {self.hourly_forecasts}"
    def __str__(self):
        return self.__repr__()
    def json(self):
        return {
            "temperature": self.get_temperature(),
            "date": str_time(self.get_date()) if type(self.get_date()) is type(datetime.now().time()) else str_date(self.get_date()),
            "kind": self.get_kind(),
            "description": self.get_description(),
            "emoji": self.get_emoji(),
            "adverse_weather": self.get_adverse_weather(),
            "hourly_forecasts": [f.json() for f in self.get_hourly_forecasts()],
        }

class Weather:

    def __init__(self):
        self.client = python_weather.Client(unit=python_weather.METRIC)
    async def get(self,city)->Forecast:
        weather = await self.client.get(city)
        daily_forecasts = list(weather.daily_forecasts)
        kind = lambda c: c.astronomy.moon_phase if hasattr(c,'astronomy') else (c.kind if hasattr(c,'kind') else None)
        create = lambda c,adverse_weather=lambda _: None: Forecast(c.temperature,c.date if hasattr(c,'date') else c.time,str(kind(c)) if kind(c) else kind(c),(c.description if hasattr(c,'description') else None),(kind(c).emoji if kind(c) else None),adverse_weather=adverse_weather(c))
        forecasts = [create(forecast) for forecast in daily_forecasts]

        def adverse_weather(hf:HourlyForecast):
            if hf.heat_index>52:
                return "heat"
            if hf.wind_gust>30:
                return "wind_gust"
            if hf.chances_of_fog>.5:
                return "fog"
            if hf.chances_of_frost>.5:
                return "frost"
            if hf.chances_of_high_temperature>.5:
                return "high_temperature"
            if hf.chances_of_rain>.5:
                return "rain"
            if hf.chances_of_snow>.5:
                return "snow"
            return None

        return [forecast.set_hourly_forecasts([create(forecast,adverse_weather) for forecast in daily_forecasts[i].hourly_forecasts]) for i,forecast in enumerate(forecasts)]