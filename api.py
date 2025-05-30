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

    api_endpoint = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&current=temperature_2m,apparent_temperature,is_day,precipitation,wind_speed_10m,wind_direction_10m,rain,snowfall&timezone=auto&wind_speed_unit={wind_unit}&temperature_unit={temp_unit}&precipitation_unit={prec_unit}"

    data = requests.get(api_endpoint).json()

    weather = {
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

def main():
    lat = 43.70643
    lon = -79.39864 

    for location in fetch_locations("t"):
        print(f"{location["name"]}: ({location["lat"]}, {location["long"]})")

if __name__ == "__main__":
    main()