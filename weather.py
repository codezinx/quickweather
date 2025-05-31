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
        # Set font and styles
        self.win.configure(background="#305CDE")
        self.style = ttk.Style()
        self.style.configure(".", font=("Calibri", 12))
        self.style.configure(".", background="#305CDE")
        self.style.configure("TLabel", foreground="white")
        self.style.layout("TMenubutton", [
            ('Menubutton.background', None),
            ('Menubutton.button', {'children':
                [('Menubutton.focus', {'children':
                    [('Menubutton.padding', {'children':
                        [('Menubutton.label', {'side': 'left'}),
                        ('Menubutton.indicator', {'side': 'right'})]
                    })]
                })]
            })]
        )
        self.style.configure("TMenubutton", foreground="white", arrowcolor="white")
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
        # Initalize latitude, longitude, and units
        self.lat = None
        self.lon = None
        self.units = "Metric"
    
    def update_weather(self, e=None):
        # Get weather data
        try:
            self.lat = self.el_location.locations[self.el_location.searchbar.current()]["lat"]
            self.lon = self.el_location.locations[self.el_location.searchbar.current()]["long"]
            self.units = self.el_units.unit.get()
            self.el_location.saved_location.set(self.el_location.location.get())
        except IndexError:
            if self.lat is None or self.lon is None:
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

        # Update background colour

        bg_color = get_weather_bg(self.weather["weather_code"], self.weather["is_day"])
        self.win.configure(background=bg_color)
        self.style.configure(".", background=bg_color)

        # Update weather icon

        self.el_mainweather.weather_icon = get_weather_icon(self.weather["weather_code"], self.weather["is_day"], (80, 80))
        self.el_mainweather.weather_img.config(image=self.el_mainweather.weather_icon)
        self.el_mainweather.weather_img.image = self.el_mainweather.weather_icon

class Location:
    def __init__(self, win):
        self.frame = ttk.Frame(win, padding=10)
        self.label = ttk.Label(self.frame, text="Location:")
        self.location = tk.StringVar()
        self.saved_location = tk.StringVar()
        self.searchbar = ttk.Combobox(self.frame, textvariable=self.location, values=())
        # After ID, prevents searchbar from being updated on every keypress
        self.after_id = None
        # Packing
        self.label.pack(side="left")
        self.searchbar.pack(fill="x", expand=True, padx=5)
        self.frame.pack(fill="x")
        # Variables to select latitute and longitude from location
        self.locations = []
        # Searchbar placeholder
        self.placeholder = "Begin by entering a city name only..."
        self.show_placeholder()
        self.searchbar.bind("<FocusIn>", self.clear_placeholder)
        self.searchbar.bind("<FocusOut>", self.show_placeholder)
        # Bind update method to searchbar
        self.searchbar.bind("<KeyRelease>", self.update)

    def clear_placeholder(self, e=None):
        if self.searchbar.get() == self.placeholder:
            self.searchbar.set("")
    
    def show_placeholder(self, e=None):
        if not self.searchbar.get() and self.saved_location.get() != "":
            self.searchbar.set(self.saved_location.get())
        elif not self.searchbar.get():
            self.searchbar.set(self.placeholder)

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
        self.mainframe = ttk.Frame(win, padding=10)
        # Variables
        self.temp = tk.StringVar(value="XX")
        self.tempunit = tk.StringVar(value="\u00b0U")
        self.weather = tk.StringVar(value="Choose a location")
        # Weather Icon
        self.weather_icon = get_weather_icon(2, True, (80, 80))
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
        self.tempunit_label.pack(pady=12)
        self.tempframe.pack(anchor="w")
        self.weather_label.pack(anchor="w")
        self.textframe.pack(padx=10)
        self.mainframe.pack()

class FeelsLike:
    def __init__(self, win):
        self.frame = ttk.Frame(win, padding=10)
        self.boldfont = ttk.Style()
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold"))
        self.feels_like = tk.StringVar(value="N/A")
        self.feels_like_text = ttk.Label(self.frame, text="Feels Like:")
        self.feels_like_label = ttk.Label(self.frame, textvariable=self.feels_like, style="Bold.TLabel")
        # Packing
        self.feels_like_text.pack(side="left") 
        self.feels_like_label.pack(side="left")
        self.frame.pack()

class Wind:
    def __init__(self, win):
        self.frame = ttk.Frame(win, padding=10)
        self.wind_get_img = Image.open("img/wind.png")
        self.wind_get_img = invert_image(self.wind_get_img)
        self.wind_get_img.thumbnail((30, 30), Image.Resampling.LANCZOS)
        self.wind_icon = ImageTk.PhotoImage(self.wind_get_img)
        self.wind_img = ttk.Label(self.frame, image=self.wind_icon)
        self.wind_img.image = self.wind_icon
        self.boldfont = ttk.Style()
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold"))
        self.wind_stat = tk.StringVar(value="Wind Stat:")
        self.wind_velocity = tk.StringVar(value="N/A")
        self.label = ttk.Label(self.frame, textvariable=self.wind_stat)
        self.velocity_label = ttk.Label(self.frame, textvariable=self.wind_velocity, style="Bold.TLabel")
        # Packing
        self.wind_img.pack(side="left", padx=5)
        self.label.pack(side="left")
        self.velocity_label.pack(side="left")
        self.frame.pack()

class Precipitation:
    def __init__(self, win):
        # Mainframe
        self.mainframe = ttk.Frame(win, padding=10)
        # Variables
        self.chance = tk.StringVar(value="N/A")
        self.prec = tk.StringVar(value="N/A")
        # Precipitation icon
        self.prec_get_img = Image.open("img/rainy.png")
        self.prec_get_img = invert_image(self.prec_get_img)
        self.prec_get_img.thumbnail((40, 40), Image.Resampling.LANCZOS)
        self.prec_icon = ImageTk.PhotoImage(self.prec_get_img)
        self.prec_img = ttk.Label(self.mainframe, image=self.prec_icon)
        self.prec_img.image = self.prec_icon
        # Bold font style
        self.boldfont = ttk.Style()
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold"))
        # Labels
        self.textframe = ttk.Frame(self.mainframe)
        self.chance_frame = ttk.Frame(self.textframe)
        self.chance_text = ttk.Label(self.chance_frame, text="Chance of Rain/Snow:")
        self.chance_label = ttk.Label(self.chance_frame, textvariable=self.chance, style="Bold.TLabel")
        self.prec_frame = ttk.Frame(self.textframe)
        self.prec_text = ttk.Label(self.prec_frame, text="Precipitation:")
        self.prec_label = ttk.Label(self.prec_frame, textvariable=self.prec, style="Bold.TLabel")
        # Packing
        self.prec_img.pack(side="left")
        self.chance_text.pack(side="left")
        self.chance_label.pack()
        self.chance_frame.pack(anchor="w")
        self.prec_text.pack(side="left")
        self.prec_label.pack()
        self.prec_frame.pack(anchor="w")
        self.textframe.pack(padx=10)
        self.mainframe.pack()

class Units:
    def __init__(self, win):
        self.frame = ttk.Frame(win, padding=10)
        self.label = ttk.Label(self.frame, text="Units:")
        self.options = ["Metric", "Imperial"]
        self.unit = tk.StringVar(value=self.options[0])
        self.dropdown = ttk.OptionMenu(self.frame, self.unit, self.options[0], *self.options)
        self.refresh = ttk.Button(self.frame, text="Refresh")
        # Packing
        self.label.pack(side="left")
        self.dropdown.pack(side="left")
        self.refresh.pack(padx=5)
        self.frame.pack(side="bottom")

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
    get_img = invert_image(get_img)    

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

def get_weather_bg(code, is_day):
    hex_code = ""

    if (code == 0 or code == 1) and is_day:
        hex_code = "#FF7518" # orange
    elif code == 0 or code == 1:
        hex_code = "#272757" # midnight blue
    elif code == 2 and is_day:
        hex_code = "#305CDE" # royal blue
    elif code == 2:
        hex_code = "#272757" # midnight blue
    elif code == 3:
        hex_code = "#909EAE" # grey
    elif code == 45 or code == 48:
        hex_code = "#909EAE" # grey
    elif code in {51, 56, 61, 66, 80}:
        hex_code = "#305CDE" # royal blue
    elif code in {53, 55, 57, 63, 65, 67, 81, 82}:
        hex_code = "#305CDE" # royal blue
    elif code in {71, 73, 75, 77, 85, 86}:
        hex_code = "#069464" # teal
    elif code in {95, 96, 99}:
        hex_code = "#435161" # dark grey
    else:
        hex_code = "#305CDE" # grey
    
    return hex_code

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