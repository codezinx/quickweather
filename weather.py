"""
Name: Adore S.
Date: 2025 Jun 6
Description: QuickWeather, simple weather app for current forecasts
"""

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageOps, ImageTk
import requests

class Weather:
    def __init__(self):
        # Initialize main window
        self.win = tk.Tk()
        self.win.title("QuickWeather")
        self.win.geometry("650x400")
        self.weather_icon = tk.PhotoImage(file="img/weather.png")
        self.win.iconphoto(False, self.weather_icon)
        # Set font
        self.style = ttk.Style()
        self.style.configure(".", font=("Calibri", 12))
        self.win.option_add("*TCombobox*Listbox*Font", ("Calibri", 12))
        self.win.option_add("*TCombobox*Font", ("Calibri", 12))
        self.win.option_add("*Menu*Font", ("Calibri", 12))
        # Initialize app components
        self.el_location = Location(self.win)
        self.el_mainweather = MainWeather(self.win)
        self.el_feelslike = FeelsLike(self.win)
        self.el_wind = Wind(self.win)
        self.el_precipitation = Precipitation(self.win)
        self.el_units = Units(self.win)
        # Update weather data on location change, unit change, or refresh
        self.el_location.searchbar.bind("<<ComboboxSelected>>", self.update_weather)
        self.el_units.unit.trace_add("write", lambda *args: self.update_weather())
        self.el_units.refresh.config(command=self.update_weather)
    
    def update_weather(self, e=None):
        # Get weather data
        try:
            self.lat = self.el_location.locations[self.el_location.searchbar.current()]["lat"]
            self.lon = self.el_location.locations[self.el_location.searchbar.current()]["long"]
            self.units = self.el_units.unit.get()
        except IndexError:
            return
        
        self.weather = fetch_weather(self.lat, self.lon, self.units)

        # Update UI with fetched weather data

        self.el_mainweather.temp.set(f"{self.weather["temp"]}")
        self.el_mainweather.tempunit.set("\u00b0C" if self.units == "Metric" else "\u00b0F")
        self.el_mainweather.weather.set(get_weather(self.weather["weather_code"], self.weather["is_day"]))
        self.el_feelslike.feels_like.set(f"{self.weather["feels_like"]} {"\u00b0C" if self.units == "Metric" else "\u00b0F"}")
        self.el_wind.wind_velocity.set(f"{self.weather["wind_speed"]} {"km/h" if self.units == "Metric" else "mph"} {get_compass_dir(self.weather["wind_dir"])}")
        self.el_wind.wind_stat.set(get_wind_stat(self.weather["wind_speed"], self.units) + ":")
        self.el_precipitation.chance.set(f"{self.weather["prec_chance"]}%")
        self.el_precipitation.prec.set(f"{self.weather["prec"]} {"mm" if self.units == "Metric" else "in"}")

        # Update weather icon

        self.el_mainweather.weather_icon = get_weather_icon(self.weather["weather_code"], self.weather["is_day"], (80, 80))
        self.el_mainweather.weather_img.config(image=self.el_mainweather.weather_icon)
        self.el_mainweather.weather_img.image = self.el_mainweather.weather_icon

class Location:
    def __init__(self, win):
        self.frame = ttk.Frame(win)
        self.label = ttk.Label(self.frame, text="Location:")
        self.location = tk.StringVar()
        self.searchbar = ttk.Combobox(self.frame, textvariable=self.location, values=())
        # After ID, prevents searchbar from being updated on every keypress
        self.after_id = None
        # Packing
        self.label.pack(side="left")
        self.searchbar.pack()
        self.frame.pack()
        # Variables to select latitute and longitude from location
        self.locations = []
        # Bind update method to searchbar
        self.searchbar.bind("<KeyRelease>", self.update)
    
    def update(self, e):
        # Cancel any previous scheduled update
        if self.after_id:
            self.frame.after_cancel(self.after_id)
        # Schedule new update after finished typing
        self.after_id = self.frame.after(500, self.do_update)

    def do_update(self):
        query = self.location.get()
        locations = fetch_locations(query)
        names = [loc["name"] for loc in locations]

        self.searchbar["values"] = names
        self.locations = locations

        # Show dropdown
        self.searchbar.event_generate("<Down>")

class MainWeather:
    def __init__(self, win):
        # Mainframe
        self.mainframe = ttk.Frame(win)
        # Variables
        self.temp = tk.StringVar(value="25")
        self.tempunit = tk.StringVar(value="\u00b0C")
        self.weather = tk.StringVar(value="Sunny")
        # Weather Icon
        self.weather_icon = get_weather_icon(0, True, (80, 80))
        self.weather_img = ttk.Label(self.mainframe, image=self.weather_icon)
        self.weather_img.image = self.weather_icon
        # Text frames and styles
        self.textframe = ttk.Frame(self.mainframe)
        self.tempframe = ttk.Frame(self.textframe)
        self.largetemp = ttk.Style().configure("Largetemp.TLabel", font=("Calibri", 35))
        # Labels
        self.temp_label = ttk.Label(self.tempframe, textvariable=self.temp, style="Largetemp.TLabel")
        self.tempunit_label = ttk.Label(self.tempframe, textvariable=self.tempunit)
        self.weather_label = ttk.Label(self.textframe, textvariable=self.weather)
        # Packing frames and weather label
        self.weather_img.pack(side="left", anchor="w")
        self.temp_label.pack(side="left")
        self.tempunit_label.pack(pady=15)
        self.tempframe.pack(anchor="w")
        self.weather_label.pack(anchor="w")
        self.textframe.pack()
        self.mainframe.pack()

class FeelsLike:
    def __init__(self, win):
        self.frame = ttk.Frame(win)
        self.feels_like = tk.StringVar(value="20 \u00b0C")
        self.feels_like_text = ttk.Label(self.frame, text="Feels Like:")
        self.feels_like_label = ttk.Label(self.frame, textvariable=self.feels_like)
        # Packing
        self.feels_like_text.pack(side="left") 
        self.feels_like_label.pack(side="left")
        self.frame.pack()

class Wind:
    def __init__(self, win):
        self.frame = ttk.Frame(win)
        self.wind_get_img = Image.open("img/wind.png")
        self.wind_get_img.thumbnail((30, 30), Image.Resampling.LANCZOS)
        self.wind_icon = ImageTk.PhotoImage(self.wind_get_img)
        self.wind_img = ttk.Label(self.frame, image=self.wind_icon)
        self.wind_img.image = self.wind_icon
        self.wind_stat = tk.StringVar(value="Windy:")
        self.wind_velocity = tk.StringVar(value="30 km/h SE")
        self.label = ttk.Label(self.frame, textvariable=self.wind_stat)
        self.velocity_label = ttk.Label(self.frame, textvariable=self.wind_velocity)
        # Packing
        self.wind_img.pack(side="left")
        self.label.pack(side="left")
        self.velocity_label.pack(side="left")
        self.frame.pack()

class Precipitation:
    def __init__(self, win):
        # Mainframe
        self.mainframe = ttk.Frame(win)
        # Variables
        self.chance = tk.StringVar(value="15%")
        self.prec = tk.StringVar(value="0 mm")
        # Precipitation icon
        self.prec_get_img = Image.open("img/rainy.png")
        self.prec_get_img.thumbnail((40, 40), Image.Resampling.LANCZOS)
        self.prec_icon = ImageTk.PhotoImage(self.prec_get_img)
        self.prec_img = ttk.Label(self.mainframe, image=self.prec_icon)
        self.prec_img.image = self.prec_icon
        # Labels
        self.textframe = ttk.Frame(self.mainframe)
        self.chance_frame = ttk.Frame(self.textframe)
        self.chance_text = ttk.Label(self.chance_frame, text="Chance of Rain/Snow:")
        self.chance_label = ttk.Label(self.chance_frame, textvariable=self.chance)
        self.prec_frame = ttk.Frame(self.textframe)
        self.prec_text = ttk.Label(self.prec_frame, text="Precipitation:")
        self.prec_label = ttk.Label(self.prec_frame, textvariable=self.prec)
        # Packing
        self.prec_img.pack(side="left")
        self.chance_text.pack(side="left")
        self.chance_label.pack()
        self.chance_frame.pack()
        self.prec_text.pack(side="left")
        self.prec_label.pack()
        self.prec_frame.pack()
        self.textframe.pack()
        self.mainframe.pack()

class Units:
    def __init__(self, win):
        self.frame = ttk.Frame(win)
        self.label = ttk.Label(self.frame, text="Units:")
        self.options = ["Metric", "Imperial"]
        self.unit = tk.StringVar(value=self.options[0])
        self.dropdown = ttk.OptionMenu(self.frame, self.unit, self.options[0], *self.options)
        self.refresh = ttk.Button(self.frame, text="Refresh")
        # Packing
        self.label.pack(side="left")
        self.dropdown.pack(side="left")
        self.refresh.pack()
        self.frame.pack()

def fetch_weather(lat, lon, units="Metric"):
    if units == "Metric":
        temp_unit = "celsius"
        wind_unit = "kmh"
        prec_unit = "mm"
    elif units == "Imperial":
        temp_unit = "fahrenheit"
        wind_unit = "mph"
        prec_unit = "inch"
    else:
        raise ValueError("Invalid units specified. Use 'metric' or 'imperial'.")

    api_endpoint = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&current=temperature_2m,apparent_temperature,is_day,precipitation,wind_speed_10m,wind_direction_10m,rain,snowfall,weather_code&timezone=auto&wind_speed_unit={wind_unit}&temperature_unit={temp_unit}&precipitation_unit={prec_unit}"

    data = requests.get(api_endpoint).json()

    weather = {
        "weather_code": data["current"]["weather_code"],
        "temp": round(data["current"]["temperature_2m"]),
        "feels_like": round(data["current"]["apparent_temperature"]),
        "is_day": data["current"]["is_day"],
        "prec": round(data["current"]["precipitation"]),
        "prec_chance": data["daily"]["precipitation_probability_max"][0],
        "wind_speed": round(data["current"]["wind_speed_10m"]),
        "wind_dir": data["current"]["wind_direction_10m"],
        "rain": round(data["current"]["rain"]),
        "snowfall": round(data["current"]["snowfall"]),
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

def get_weather_icon(code, is_day, size):
    img_path = ""

    if (code == 0 or code == 1) and is_day:
        img_path = "img/sunny.png"
    elif code == 0 or code == 1:
        img_path = "img/clear_night.png"
    elif code == 2 and is_day:
        img_path = "img/partly_cloudy.png"
    elif code == 2:
        img_path = "img/partly_cloudy_night.png"
    elif code == 3:
        img_path = "img/cloudy.png"
    elif code == 45 or code == 48:
        img_path = "img/foggy.png"
    elif code in {51, 56, 61, 66, 80}:
        img_path = "img/light_rain.png"
    elif code in {53, 55, 57, 63, 65, 67, 81, 82}:
        img_path = "img/rainy.png"
    elif code in {71, 73, 75, 77, 85, 86}:
        img_path = "img/snowy.png"
    elif code in {95, 96, 99}:
        img_path = "img/thunderstorm.png"
    else:
        img_path = "img/cloudy.png"
    
    get_img = Image.open(img_path)
    # get_img = invert_image(get_img)    

    get_img.thumbnail(size, Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(get_img)

def invert_image(img: Image.Image):
    if img.mode == "P":
        img = img.convert("RGBA")

    if img.mode == "RGBA":
        r, g, b, a = img.split()
        rgb_img = Image.merge("RGB", (r, g, b))
        inv_img = ImageOps.invert(rgb_img)
        r2, g2, b2 = inv_img.split()
        return Image.merge("RGBA", (r2, g2, b2, a))
    else:
        return ImageOps.invert(img)

def get_compass_dir(deg):
    if deg < 0 or deg > 360:
        raise ValueError("Invalid degree value. Must be between 0 and 360.")

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] 
    index = round(deg / 45) % 8

    return directions[index]

def get_wind_stat(wind_speed, units="Metric"):
    wind_stats = ["No Wind", "Slightly Windy", "Windy", "Very Windy", "Stormy", "Violent Storm"]

    if units == "Metric": # km/h
        if 0 <= wind_speed < 1:
            return wind_stats[0]
        elif 1 <= wind_speed < 16:
            return wind_stats[1]
        elif 16 <= wind_speed < 31:
            return wind_stats[2]
        elif 31 <= wind_speed < 51:
            return wind_stats[3]
        elif 51 <= wind_speed < 76:
            return wind_stats[4]
        elif wind_speed >= 76:
            return wind_stats[5]
        else:
            raise ValueError("Invalid wind speed value.")
    elif units == "Imperial": # mph
        if 0 <= wind_speed < 1:
            return wind_stats[0]
        elif 1 <= wind_speed < 10:
            return wind_stats[1]
        elif 10 <= wind_speed < 19:
            return wind_stats[2]
        elif 19 <= wind_speed < 32:
            return wind_stats[3]
        elif 32 <= wind_speed < 46:
            return wind_stats[4]
        elif wind_speed >= 46:
            return wind_stats[5]
        else:
            raise ValueError("Invalid wind speed value.")

def main():
    app = Weather()
    app.win.mainloop()

if __name__ == "__main__":
    main()