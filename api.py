import requests

def fetch_weather(lat, lon, units="metric"):
    if units == "metric":
        temp_unit = "celsius"
        wind_unit = "kmh"
        prec_unit = "mm"
    elif units == "imperial":
        temp_unit = "fahrenheit"
        wind_unit = "mph"
        prec_unit = "inch"
    else:
        raise ValueError("Invalid units specified. Use 'metric' or 'imperial'.")

    api_endpoint = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&current=temperature_2m,apparent_temperature,is_day,precipitation,wind_speed_10m,wind_direction_10m,rain,snowfall,weather_code&timezone=auto&wind_speed_unit={wind_unit}&temperature_unit={temp_unit}&precipitation_unit={prec_unit}"

    data = requests.get(api_endpoint).json()

    weather = {
        "weather_code": data["current"]["weather_code"],
        "temp": data["current"]["temperature_2m"],
        "feels_like": data["current"]["apparent_temperature"],
        "is_day": data["current"]["is_day"],
        "prec": data["current"]["precipitation"],
        "prec_chance": data["daily"]["precipitation_probability_max"][0],
        "wind_speed": data["current"]["wind_speed_10m"],
        "wind_dir": data["current"]["wind_direction_10m"],
        "rain": data["current"]["rain"],
        "snowfall": data["current"]["snowfall"],
    }

    return weather

def fetch_locations(query):
    api_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language=en&format=json"

    data = requests.get(api_endpoint).json()

    locations = []

    try:
        for location in data["results"]:
            state = location.get("admin1", "")
            locations.append({
                "name": f"{location["name"]}, {f"{state}, " if state != " " else ""}{location["country"]}",
                "lat": location["latitude"],
                "long": location["longitude"]
            })
    except KeyError:
        pass
    
    return locations

def get_weather(code, is_day):
    weather = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Cloudy",
        45: "Foggy",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        56: "Light Freezing Drizzle",
        57: "Freezing Drizzle",
        61: "Slightly Rainy",
        63: "Rainy",
        65: "Heavily Rainy",
        66: "Light Freezing Rain",
        67: "Freezing Rain",
        71: "Lightly Snowy",
        73: "Snowy",
        75: "Heavily Snowy",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Snow Showers",
        95: "Thunderstorm",
        96: "Light Thunderstorms with Hail",
        99: "Thunderstorm with Hail"
    }

    if is_day:
        weather.update({
            0: "Sunny",
            1: "Mainly Sunny"
        })
    
    return weather.get(code, "Unknown")

def get_compass_dir(deg):
    if deg < 0 or deg > 360:
        raise ValueError("Invalid degree value. Must be between 0 and 360.")

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] 
    index = round(deg / 45) % 8

    return directions[index]

def main():
    lat = 43.70643
    lon = -79.39864 

    weather = fetch_weather(lat, lon, "metric")

    for data, value in weather.items():
        if data == "weather_code":
            print(f"weather: {get_weather(value, weather['is_day'])}")
        elif data == "wind_dir":
            print(f"wind_dir: {get_compass_dir(value)}")
        else:
            print(f"{data}: {value}")

if __name__ == "__main__":
    main()