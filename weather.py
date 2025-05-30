"""
Name: Adore S.
Date: 2025 Jun 6
Description: QuickWeather, simple weather app for current forecasts
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests

class Weather:
    def __init__(self):
        # Initialize main window
        self.win = tk.Tk()
        self.win.title("QuickWeather")
        self.win.geometry("650x400")
        self.weather_icon = tk.PhotoImage(file="img/weather.png")
        self.win.iconphoto(False, self.weather_icon)
        # Initialize app components
        self.el_location = Location(self.win)
        self.el_mainweather = MainWeather(self.win)
        self.el_feelslike = FeelsLike(self.win)
        self.el_wind = Wind(self.win)
        self.el_precipitation = Precipitation(self.win)
        self.el_units = Units(self.win)
        # Update weather data
        self.el_location.searchbar.bind("<<ComboboxSelected>>", self.update_weather)
    
    def update_weather(self, e):
        # Get weather data
        try:
            self.lat = self.el_location.locations[self.el_location.searchbar.current()]["lat"]
            self.lon = self.el_location.locations[self.el_location.searchbar.current()]["long"]
            self.units = self.el_units.unit.get()
            print("Lat:", self.lat)
            print("Lon:", self.lon)
            print("Units:", self.units)
        except IndexError:
            pass
        

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
        self.weather_icon = ImageTk.PhotoImage(Image.open("img/sunnyk.png").resize((80, 80)))
        self.weather_img = ttk.Label(self.mainframe, image=self.weather_icon)
        self.weather_img.image = self.weather_icon
        # Text frames and styles
        self.textframe = ttk.Frame(self.mainframe)
        self.tempframe = ttk.Frame(self.textframe)
        self.largetemp = ttk.Style().configure("Largetemp.TLabel", font=("Segoe UI", 35))
        # Labels
        self.temp_label = ttk.Label(self.tempframe, textvariable=self.temp, style="Largetemp.TLabel")
        self.tempunit_label = ttk.Label(self.tempframe, textvariable=self.tempunit)
        self.weather_label = ttk.Label(self.textframe, textvariable=self.weather)
        # Packing frames and weather label
        self.weather_img.pack(side="left", anchor="w")
        self.temp_label.pack(side="left")
        self.tempunit_label.pack(pady=15)
        self.tempframe.pack()
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
        self.wind_icon = ImageTk.PhotoImage(Image.open("img/wind.png").resize((30, 30)))
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
        self.prec_icon = ImageTk.PhotoImage(Image.open("img/rain.png").resize((40, 40)))
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
    app = Weather()
    app.win.mainloop()

if __name__ == "__main__":
    main()