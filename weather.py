"""
Name: Adore S.
Date: 2025 Jun 6
Description: QuickWeather, simple weather app for current forecasts
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk
import requests

class Weather:
    """
    The main class for the QuickWeather application. This class houses the main window and initializes all components of the app.
    """

    def __init__(self):
        """
        Function to initialize Weather component and all of QuickWeather's components.
        """

        # Stage I: Initialize the main window

        self.win = tk.Tk() # Initalize main window
        self.win.title("QuickWeather") # Set title
        self.win.geometry("650x400") # Set default window size
        self.weather_icon = tk.PhotoImage(file="img/weather.png") # Get weather icon
        self.win.iconphoto(False, self.weather_icon) # Set application icon to weather icon

        # Stage II: Set font and styles

        # Initalize default style
        self.style = ttk.Style()

        # Set default font to Calibri, size 12
        self.style.configure(".", font=("Calibri", 12))
        self.win.option_add("*TCombobox*Listbox*Font", ("Calibri", 12))
        self.win.option_add("*TCombobox*Font", ("Calibri", 12))
        self.win.option_add("*Menu*Font", ("Calibri", 12))

        # Set default background colour to royal blue
        self.style.configure(".", background="#305CDE")
        self.win.configure(background="#305CDE")
        
        # Set default font and foreground colour to white
        self.style.configure("TLabel", foreground="white")
        # The entire code for TMenubutton is needed to make the dropdown arrow white
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

        # Stage III: Initialize app components

        self.el_location = Location(self.win) # Initialize location searchbar
        self.el_mainweather = MainWeather(self.win) # Initalize main weather components (temperature, weather, and icon)
        self.el_feelslike = FeelsLike(self.win) # Initalize feels like temperature
        self.el_wind = Wind(self.win) # Initalize wind speed and direction
        self.el_precipitation = Precipitation(self.win) # Initalize precipitation data
        self.el_units = Units(self.win) # Initalize units dropdown and refresh button

        # Stage IV: Update weather data on location change, unit change, or refresh

        self.el_location.searchbar.bind("<<ComboboxSelected>>", self.update_weather) # Update on location change (searchbar select)
        self.el_units.unit.trace_add("write", lambda *args: self.update_weather()) # Update on unit change (Metric / Imperial)
        self.el_units.refresh.config(command=self.update_weather) # Update on refresh button click

        # Stage IVa: Initalize default values for latitude, longitude, and units (before any location is selected)

        self.lat = None
        self.lon = None
        self.units = "Metric"
    
    def update_weather(self, e=None):
        """
        Updates weather data based on the selected location and units.

        :param e: Event object, if any (default is None)
        """

        # Stage I: Get weather data

        try:
            # Only update weather data if a location is selected in the searchbar

            if self.el_location.searchbar.current() >= 0:
                self.lat = self.el_location.locations[self.el_location.searchbar.current()]["lat"] # Set latitude to selected location's latitude
                self.lon = self.el_location.locations[self.el_location.searchbar.current()]["long"] # Set longitude to selected location's longitude
                self.el_location.saved_location.set(self.el_location.location.get()) # Save the current location name in case of a refresh
            elif self.lat == None or self.lon == None:
                return # If there is no selected location, do nothing
            # If there is a location but no selected value, use the saved location and update units
        except IndexError:
            if self.lat == None or self.lon == None:
                return # If there is no selected location, do nothing
            # If there is a location but no selected value, use the saved location and update units
        
        self.units = self.el_units.unit.get() # Get selected unit type from dropdown
        self.weather = fetch_weather(self.lat, self.lon, self.units) # Fetch weather data

        # Stage IIa: Update UI text with fetched weather data

        # Set temperature variable to current temperature
        self.el_mainweather.temp.set(f"{self.weather['temp']}")
        # Set temperature unit variable to Celsius if units are Metric, and Fahrenheit if units are Imperial
        self.el_mainweather.tempunit.set("°C" if self.units == "Metric" else "°F")
        # Set weather variable to current weather description
        self.el_mainweather.weather.set(get_weather(self.weather["weather_code"], self.weather["is_day"]))
        # Set feels like temperature variable to current feels like temperature
        # Also set the unit to Celsius if units are Metric, and Fahrenheit if units are Imperial
        self.el_feelslike.feels_like.set(f"{self.weather['feels_like']} {'°C' if self.units == 'Metric' else '°F'}")
        # Set vind velocity variable to current wind speed and cardinal (compass) direction
        # Also set to unit to km/h if units are Metric, else set unit to mph
        self.el_wind.wind_velocity.set(f"{self.weather['wind_speed']} {'km/h' if self.units == 'Metric' else 'mph'} {get_compass_dir(self.weather['wind_dir'])}")
        # Set wind status variable to a wind status description based on wind speed
        self.el_wind.wind_stat.set(get_wind_stat(self.weather["wind_speed"], self.units) + ":")
        # Set precipitation chance variable to the likelihood of rain or snow
        self.el_precipitation.chance.set(f"{self.weather['prec_chance']}%")
        # Set precipitation variable to the amount of precipitation in mm if using Metric units, else in inches.
        self.el_precipitation.prec.set(f"{self.weather['prec']} {'mm' if self.units == 'Metric' else 'in'}")

        # Stage IIb: Update background colour based on weather

        bg_color = get_weather_bg(self.weather["weather_code"], self.weather["is_day"]) # Get background colour
        self.win.configure(background=bg_color) # Set background colour of window
        self.style.configure(".", background=bg_color) # Set background colour of everything else

        # Stage IIIc: Update weather icon

        # Get appropriate weather icon based on weather
        self.el_mainweather.weather_icon = get_weather_icon(self.weather["weather_code"], self.weather["is_day"], (80, 80))
        # Set the weather icon's component to display the retrieved weather icon
        self.el_mainweather.weather_img.config(image=self.el_mainweather.weather_icon)
        self.el_mainweather.weather_img.image = self.el_mainweather.weather_icon

class Location:
    """
    Class that houses the components needed to get the desired location from the user.
    """
    def __init__(self, win: tk.Tk):
        """
        Function that initializes all the components needed to get the location from the user.

        :param tk.Tk win: the application's main window
        """

        # Stage I: Initialize frame for location components, with a padding of 10px

        self.frame = ttk.Frame(win, padding=10)

        # Stage II: Initialize variables to store the searchbar's components (location) and the saved location.

        self.location = tk.StringVar()
        self.saved_location = tk.StringVar()

        # Stage III: Initialize "Location:" label and the searchbar to search for a valid location (city)

        self.label = ttk.Label(self.frame, text="Location:") # Initialize label that says "Location:"
        self.searchbar = ttk.Combobox(self.frame, textvariable=self.location, values=()) # Initialize the searchbar (ComboBox) 

        # Stage IV: Pack all the components for display

        self.label.pack(side="left") # Pack "Location:" label to the left side
        self.searchbar.pack(fill="x", expand=True, padx=5) # Pack searchbar beside label, expand it so it takes up all the width available
        self.frame.pack(fill="x") # Pack the location frame. Expand it so it takes up all the width available.

        # Stage V: Get a list of valid locations when user types in a location

        # Array of dictionaries with name, latitude, and longitude to select latitute and longitude from location
        self.locations = []
        # After ID, keeps track of updates, used to prevent searchbar from being updated on every keypress
        self.after_id = None

        # Stage Va: Add a placeholder to the searchbar.
        self.placeholder = "Begin by entering a city name only..." # The searchbar's default placeholder
        self.show_placeholder() # Show the placeholder when program is opened
        self.searchbar.bind("<FocusIn>", self.clear_placeholder) # Clear the placeholder when the searchbar is selected
        self.searchbar.bind("<FocusOut>", self.show_placeholder) # Show the saved location or the placeholder when the searchbar is deselected

        # Bind update method to searchbar (Stage V)
        self.searchbar.bind("<KeyRelease>", self.update) # Update the location options of the searchbar after the user is finished typing a city name

    def clear_placeholder(self, e=None):
        """
        Clears the placeholder from the searchbar.

        :param e: Event object, if any
        """

        if self.searchbar.get() == self.placeholder: # If the placeholder is in the searchbar,
            self.searchbar.set("") # Get rid of it
    
    def show_placeholder(self, e=None):
        """
        Show the saved location in the searchbar if there is one, otherwise show the placeholder.

        Only populates searchbar with either the location or placeholder if searchbar is empty.

        :param e: Event object, if any
        """

        # If the search bar is empty and there is a saved location (location has already been selected by user),
        if not self.searchbar.get() and self.saved_location.get() != "":
            # Populate searchbar with saved location
            self.searchbar.set(self.saved_location.get())
        elif not self.searchbar.get(): # Otherwise if the search bar is empty,
            # Populate searchbar with placeholder
            self.searchbar.set(self.placeholder)

    def update(self, e):
        """
        Updates the searchbar with a list of valid locations after the user is done typing.

        NOTE: This function does not do the updating itself; instead, it calls do_update to update the search results.

        :param e: Event object
        """

        # Cancel any previous scheduled update if there is one
        if self.after_id:
            self.frame.after_cancel(self.after_id)
        # Schedule new update to update searchbar after user is finished typing (500 ms delay)
        self.after_id = self.frame.after(500, self.do_update)

    def do_update(self):
        """
        Updates the searchbar with a list of valid locations based on the user's input
        """

        # Stage I: Get valid locations from user input

        query = self.location.get() # Get the user's search query (input)
        locations = fetch_locations(query) # Get the list of valid locations based on the query
        names = [loc["name"] for loc in locations] # Make a list with just the location names from the list locations

        # Stage II: Populate searchbar options and locations list with locations

        self.searchbar["values"] = names # Populate searchbar options with valid locations
        self.locations = locations # Fill locations array with list of dictionaries that incl. the location name, latitude, and longitude

        # Stage III: Show dropdown to user after he/she's finished typing

        self.searchbar.event_generate("<Down>")

class MainWeather:
    """
    Class that houses all the components for the main weather display.

    This includes the current temperature and weather.
    """
    def __init__(self, win: tk.Tk):
        """
        Function that initializes all the components for the main weather display.

        :param tk.Tk win: The main window
        """

        # Stage I: Initialize the main frame for all main weather components

        self.mainframe = ttk.Frame(win, padding=10)

        # Stage II: Initialize key variables, like the current temperature, temp. unit, and weather, and their default values

        self.temp = tk.StringVar(value="XX") # Current temperature
        self.tempunit = tk.StringVar(value="°U") # Temperature unit
        self.weather = tk.StringVar(value="Choose a location") # Current weather description (1-4 words)

        # Stage III: Initialize the weather icon

        self.weather_icon = get_weather_icon(2, 1, (80, 80)) # Get the default weather icon (cloudy)
        self.weather_img = ttk.Label(self.mainframe, image=self.weather_icon) # Display the weather icon in the main frame
        self.weather_img.image = self.weather_icon # Makes sure the weather icon is actually displayed

        # Stage IV: Initialize frames and styles needed to display the temperature and weather

        self.textframe = ttk.Frame(self.mainframe) # Frame that houses all the main weather components besides the icon
        self.tempframe = ttk.Frame(self.textframe) # Frame that houses the temperature and the temperature unit labels
        self.largetemp = ttk.Style().configure("Largetemp.TLabel", font=("Calibri", 35)) # Initalize style to show the current temp. in a large font

        # Stage IV: Initialize the labels that will show the temperature, unit, and weather

        self.temp_label = ttk.Label(self.tempframe, textvariable=self.temp, style="Largetemp.TLabel") # Shows temp. in large font
        self.tempunit_label = ttk.Label(self.tempframe, textvariable=self.tempunit) # Shows temp. unit
        self.weather_label = ttk.Label(self.textframe, textvariable=self.weather) # Shows weather description

        # Stage V: Pack all the components

        self.weather_img.pack(side="left", anchor="w") # Pack the weather icon to the left of the text components
        self.temp_label.pack(side="left") # Pack the temperature to be to the left of the temp. unit
        self.tempunit_label.pack(pady=12) # Pack the temp. unit with a vertical padding of 12 to appear level to the temp.
        self.tempframe.pack(anchor="w") # Pack the temp. frame beside the weather icon
        self.weather_label.pack(anchor="w") # Pack the weather label below the icon and temp., leaning left
        self.textframe.pack(padx=10) # Pack the text frame (text comp.) with a horiz. padding of 10 (ensures gap between icon and text)
        self.mainframe.pack() # Pack the main frame

class FeelsLike:
    """
    Class that houses the components to show the "Feels like" temp.
    """
    def __init__(self, win: tk.Tk):
        """
        Initialize "Feels like" components

        :param tk.Tk win: The main window
        """
        
        # Stage I: Initialize "Feels like" frame

        self.frame = ttk.Frame(win, padding=10)

        # Stage II: Initialize bold font for the "feels like" temp.

        self.boldfont = ttk.Style()
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold"))

        # Stage III: Initalize variables and labels to show "feels like" temperature

        self.feels_like = tk.StringVar(value="N/A") # Stores "feels like" temp.
        self.feels_like_text = ttk.Label(self.frame, text="Feels like:") # Label that shows "Feels like:"
        self.feels_like_label = ttk.Label(self.frame, textvariable=self.feels_like, style="Bold.TLabel") # Shows "feels like" temp. in bold font

        # Stage IV: Pack all the components

        self.feels_like_text.pack(side="left") # Pack "Feels like:" text
        self.feels_like_label.pack(side="left") # ... and "feels like" temp. beside each other
        self.frame.pack() # Pack the "feels like" frame

class Wind:
    """
    Class that houses the components to show the current wind conditions.
    """
    def __init__(self, win: tk.Tk):
        """
        Initialize components to show current wind conditions.

        :param tk.Tk win: The main window
        """

        # Stage I: Initialize the main frame

        self.frame = ttk.Frame(win, padding=10)

        # Stage II: Initialize the wind icon

        self.wind_get_img = Image.open("img/wind.png") # Get the wind icon's image
        self.wind_get_img = invert_image(self.wind_get_img) # Invert the wind icon's colours (to white)
        self.wind_get_img.thumbnail((30, 30), Image.Resampling.LANCZOS) # Resize wind icon to fit inside 30 px x 30 px
        self.wind_icon = ImageTk.PhotoImage(self.wind_get_img) # Set the wind icon to the wind icon's image
        self.wind_img = ttk.Label(self.frame, image=self.wind_icon) # Set a component to display the wind icon
        self.wind_img.image = self.wind_icon # Make sure the wind icon is actually displayed

        # Stage III: Set up the bold font for the wind velocity

        self.boldfont = ttk.Style() # Initialize bold font style
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold")) # Set bold font style to have a bold font

        # Stage IV: Initialize the variables to store the wind status and wind velocity

        self.wind_stat = tk.StringVar(value="Wind Stat:") # Stores wind statues (i.e. Slightly Windy)
        self.wind_velocity = tk.StringVar(value="N/A") # Stores wind speed and its compass direction

        # Stage V: Initialize the labels to display the wind status and velocity

        self.label = ttk.Label(self.frame, textvariable=self.wind_stat) # Displays wind status
        self.velocity_label = ttk.Label(self.frame, textvariable=self.wind_velocity, style="Bold.TLabel") # Shows wind velocity in bold font

        # Stage VI: Pack all the components

        self.wind_img.pack(side="left", padx=5) # Pack the wind icon,
        self.label.pack(side="left") # wind status label,
        self.velocity_label.pack(side="left") # and wind velocity label side-by-side
        self.frame.pack() # Pack the main frame

class Precipitation:
    """
    Class that houses the components to display the precipitation and its chance of happening.
    """
    def __init__(self, win: tk.Tk):
        """
        Initialize precipitation components.

        :param tk.Tk win: The main window
        """

        # Stage I: Initialize the mainframe

        self.mainframe = ttk.Frame(win, padding=10)

        # Stage II: Initialize variables to store chance of precipitation and precipitation

        self.chance = tk.StringVar(value="N/A") # Stores chance of precipitation (%)
        self.prec = tk.StringVar(value="N/A") # Stores precipitation rate (mm / in)

        # Stage III: Initialize precipitation icon

        self.prec_get_img = Image.open("img/rainy.png") # Get precipitation icon's image
        self.prec_get_img = invert_image(self.prec_get_img) # Invert precipitation icon (to white)
        self.prec_get_img.thumbnail((40, 40), Image.Resampling.LANCZOS) # Resize the icon so it fits in 40 px x 40 px
        self.prec_icon = ImageTk.PhotoImage(self.prec_get_img) # Set the precipitation icon to the precipitation icon's image
        self.prec_img = ttk.Label(self.mainframe, image=self.prec_icon) # Set a component to display the precipitation icon
        self.prec_img.image = self.prec_icon # Make sure the precipitation icon is displayed

        # Stage IV: Set up bold font style for precipitation values

        self.boldfont = ttk.Style() # Initialize bold font style
        self.boldfont.configure("Bold.TLabel", font=("Calibri", 12, "bold")) # Set bold font style to have bold font

        # Stage V: Initalize components to display precipitation data

        # Stage Va: Initialize the component that houses all the text components of Precipitation

        self.textframe = ttk.Frame(self.mainframe)

        # Stage Vb: Initialize a frame, and two labels to show the chance of precipitation

        self.chance_frame = ttk.Frame(self.textframe) # Frame for chance of rain/snow
        self.chance_text = ttk.Label(self.chance_frame, text="Chance of Rain/Snow:") # Label that says "Chance of Rain/Snow:"
        self.chance_label = ttk.Label(self.chance_frame, textvariable=self.chance, style="Bold.TLabel") # Shows the chance of rain/snow in bold font

        # Stage Vc: Initialize a frame, and two labels to show the current precipitation

        self.prec_frame = ttk.Frame(self.textframe) # Frame for precipitation
        self.prec_text = ttk.Label(self.prec_frame, text="Precipitation:") # Label that says "Precipitation:"
        self.prec_label = ttk.Label(self.prec_frame, textvariable=self.prec, style="Bold.TLabel") # Shows the precipitation level in bold font

        # Stage VI: Pack all the components

        self.prec_img.pack(side="left") # Pack the precipitation image to the left of all text
        self.chance_text.pack(side="left") # Pack the "Chance of Rain/Snow:" label to the left of the chance value
        self.chance_label.pack() # Pack the label that shows the chance of precipitation
        self.chance_frame.pack(anchor="w") # Pack the chance of precipitation frame, leaning leftwards
        self.prec_text.pack(side="left") # Pack the "Precipitation:" label to the label of the actual value
        self.prec_label.pack() # Pack the label that shows the precipitation level
        self.prec_frame.pack(anchor="w") # Pack the precipitation frame, leaning leftwards
        self.textframe.pack(padx=10) # Pack the textual frame with a gap horizontally of 10 px
        self.mainframe.pack() # Pack the main frame

class Units:
    """
    Class that houses the unit selector and refresh button
    """
    def __init__(self, win: tk.Tk):
        """
        Initialize the unit selector and refresh button

        :param tk.Tk win: The main window
        """

        # Stage I: Initialize the main frame

        self.frame = ttk.Frame(win, padding=10)

        # Stage II: Initialize the unit selector

        self.label = ttk.Label(self.frame, text="Units:") # Label that says "Units:"
        self.options = ["Metric", "Imperial"] # Options for the unit selector (Metric or Imperial)
        self.unit = tk.StringVar(value=self.options[0]) # Stores the selected unit (Metric by default)
        self.dropdown = ttk.OptionMenu(self.frame, self.unit, self.options[0], *self.options) # The actual unit selector dropdown

        # Stage III: Initialize the refresh button

        self.refresh = ttk.Button(self.frame, text="Refresh")

        # Stage IV: Pack all the components

        self.label.pack(side="left") # Pack the "Units:" label,
        self.dropdown.pack(side="left") # the dropdown,
        self.refresh.pack(padx=5) # and the refresh button w/ a horiz. padding of 5 px. side-by-side
        self.frame.pack(side="bottom") # Pack the main frame

def fetch_weather(lat: float, lon: float, units="Metric"):
    """
    Fetches the current weather from Open-Meteo in the specified set of units using latitude and longitude.

    :param float lat: The latitude
    :param float lon: The longitude
    :param str units: The type of units; can only be: "Metric", "Imperial"
    """

    # Stage I: Determine the appropriate temperature, wind speed, and precipitation unit based on whether units are metric or imperial

    if units == "Metric":
        temp_unit = "celsius"
        wind_unit = "kmh"
        prec_unit = "mm" # Precipitation unit
    elif units == "Imperial":
        temp_unit = "fahrenheit"
        wind_unit = "mph"
        prec_unit = "inch" # Precipitation unit
    else:
        raise ValueError("Invalid units specified. Use 'metric' or 'imperial'.")

    # Stage II: Fetch the relevant weather data from Open-Meteo using the specificed latitude, longitude, and units

    api_endpoint = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_probability_max&current=temperature_2m,apparent_temperature,is_day,precipitation,wind_speed_10m,wind_direction_10m,rain,snowfall,weather_code&timezone=auto&wind_speed_unit={wind_unit}&temperature_unit={temp_unit}&precipitation_unit={prec_unit}"

    data = requests.get(api_endpoint).json() # Weather data returned as a large dictionary

    # Stage III: Format the data so that only the data required is returned, in a developer-friendly format

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

def fetch_locations(query: str):
    """
    Fetches the list of valid locations (typically cities) from Open-Meteo using the user's search query

    NOTE: Open-Meteo can fetch valid locations using the city name only (i.e. Toronto). It somehow cannot fetch information with more than the city (i.e. Toronto, Ontario)

    :param str query: The search query
    """

    # Stage I: Fetch 10 valid locations from Open-Meteo based on the search query

    api_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language=en&format=json"

    data = requests.get(api_endpoint).json() # Data returned as large messy dictionary

    # Stage II: Organize the valid locations into a list of nice dictionaries where the name, latitude, and longitude are stored

    locations = [] # List of valid locations

    try:
        for location in data["results"]: # For every location,
            state = location.get("admin1", "") # Get the state / province from key 'admin1', and add...
            locations.append({
                "name": f"{location['name']}, {f'{state}, ' if state else ''}{location['country']}", # the name (City, State/Province, Country)
                "lat": location["latitude"], # the latitude
                "long": location["longitude"] # the longitude
            })
            # ... to the locations list
    except KeyError:
        pass # Return an empty list if there is no data
    
    return locations

def get_weather(code: int, is_day: int) -> str:
    """
    Get the appropriate weather description from a WMO weather code (returned by Open-Meteo)

    :param int code: The WMO weather code
    :param int is_day: A value stating whether it is: 1 (day) or 0 (night)
    """

    # Stage I: Initialize a dictionary that stores the WMO weather code and its description as pairs

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

    # Stage II: If it is day, update 'Clear' and 'Mainly Clear' in the dictionary above to be 'Sunny' and 'Mainly Sunny'

    if is_day:
        weather.update({
            0: "Sunny",
            1: "Mainly Sunny"
        })

    # Stage III: Return the weather description or "Unknown" if code is not listed
    
    return weather.get(code, "Unknown")

def get_weather_icon(code: int, is_day: int, size: tuple):
    """
    Get the appropriate weather icon from a WMO weather code (returned by Open-Meteo)

    :param int code: The WMO weather code
    :param int is_day: Is it 0 (night) or 1 (day)?
    :param tuple[int, int] size: The size constraints of the image: (width, height)
    :rtype: ImageTk.PhotoImage
    """

    # Stage I: Get the appropritate weather icon's path

    img_path = ""

    if (code == 0 or code == 1) and is_day: # If it's sunny or mainly sunny
        img_path = "img/sunny.png" # Set image path to the "sunny" image, rest of img_path sets self-explanatory
    elif code == 0 or code == 1: # If it's clear or mainly clear and it's night
        img_path = "img/clear_night.png"
    elif code == 2 and is_day: # If it's partly cloudy and it's daytime
        img_path = "img/partly_cloudy.png" # Path of partly cloudy icon with sun
    elif code == 2: # If it's partly cloudy and it's nighttime
        img_path = "img/partly_cloudy_night.png" # Path of partly cloudy icon with moon
    elif code == 3: # If it's cloudy
        img_path = "img/cloudy.png"
    elif code == 45 or code == 48: # If it's foggy
        img_path = "img/foggy.png"
    elif code in {51, 56, 61, 66, 80}: # If it's lightly raining
        img_path = "img/light_rain.png"
    elif code in {53, 55, 57, 63, 65, 67, 81, 82}: # If it's rainy
        img_path = "img/rainy.png"
    elif code in {71, 73, 75, 77, 85, 86}: # If it's snowy
        img_path = "img/snowy.png"
    elif code in {95, 96, 99}: # If there is a thunderstorm
        img_path = "img/thunderstorm.png"
    else: # Show a cloud if the code is not listed
        img_path = "img/cloudy.png"
    
    get_img = Image.open(img_path) # Open the appropriate icon specified in img_path
    get_img = invert_image(get_img) # Invert the icon (to white)

    get_img.thumbnail(size, Image.Resampling.LANCZOS) # Resize the icon to fit in the specified size

    return ImageTk.PhotoImage(get_img) # Return the image as an ImageTk.PhotoImage object

def invert_image(img: Image.Image):
    """
    Invert or get the negative of an image.

    :param Image.Image img: The image object
    """

    # If the image is in paletissed mode, convert to RGBA mode (A = alpha)

    if img.mode == "P":
        img = img.convert("RGBA")

    # If the image is in RGBA mode

    if img.mode == "RGBA":
        r, g, b, a = img.split() # Split the indiviual colour channels
        rgb_img = Image.merge("RGB", (r, g, b)) # Merge all the colour channels except for alpha (transparency)
        inv_img = ImageOps.invert(rgb_img) # Invert (make negative) the merged image w/o transparency
        r2, g2, b2 = inv_img.split() # Split the colour channels of the inverted image
        return Image.merge("RGBA", (r2, g2, b2, a)) # Merge the colour channels and the transparency into a final image, then return it
    else:
        return ImageOps.invert(img) # Invert the image and return it

def get_weather_bg(code: int, is_day: int) -> str:
    """
    Return the hex code of the appropriate background colour for the current weather using a WMO code

    :param int code: The WMO weather code
    :param int is_day: Is 0 (night) or 1 (day)?
    """

    hex_code = ""

    if (code == 0 or code == 1) and is_day: # If it's sunny or mainly sunny
        hex_code = "#FF7518" # set hex_code to orange
    elif code == 0 or code == 1: # If it's night and clear or mainly clear
        hex_code = "#272757" # midnight blue
    elif code == 2 and is_day: # If it's partly cloudy and it's daytime
        hex_code = "#305CDE" # royal blue
    elif code == 2: # If it's partly cloudy and it's nighttime
        hex_code = "#272757" # midnight blue
    elif code == 3: # If it's cloudy
        hex_code = "#909EAE" # grey
    elif code == 45 or code == 48: # If it's foggy
        hex_code = "#909EAE" # grey
    elif code in {51, 56, 61, 66, 80}: # If it's lightly raining
        hex_code = "#305CDE" # royal blue
    elif code in {53, 55, 57, 63, 65, 67, 81, 82}: # If it's raining
        hex_code = "#305CDE" # royal blue
    elif code in {71, 73, 75, 77, 85, 86}: # If it's snowing
        hex_code = "#069464" # teal
    elif code in {95, 96, 99}: # If there is a thunderstorm
        hex_code = "#435161" # dark grey
    else: # Default colour for unrecognized weather
        hex_code = "#305CDE" # grey
    
    return hex_code

def get_compass_dir(deg: float) -> str:
    """
    Returns one of 8 compass directions (N, NE, E, SE, S, SW, N, NW) from a bearing angle in degrees

    :param float deg: The bearing angle (0 deg = N, rotates clockwise, 90 deg = E), must be between 0 and 360
    """

    # Bearing angle must be between 0 and 360

    if deg < 0 or deg > 360:
        raise ValueError("Invalid degree value. Must be between 0 and 360.")

    # Return appropriate compass direction based on bearing angle

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] 
    # Round to the closest bearing angle associated with directions above, then return appropriate index for directions above
    index = round(deg / 45) % 8 

    return directions[index]

def get_wind_stat(wind_speed: float, units="Metric") -> str:
    """
    Get the appropriate wind status from the wind speed

    :param float wind_speed: The wind speed in km/h if Metric or mph if Imperial
    :param str units: Type of Units: "Metric" or "Imperial"
    """

    wind_stats = ["No Wind", "Slightly Windy", "Windy", "Very Windy", "Stormy", "Violent Storm"]

    if units == "Metric": # If the wind speed is in km/h
        if 0 <= wind_speed < 1: # Wind speed between 0 km/h (incl.) and 1 km/h (excl.), and so on
            return wind_stats[0] # Return "No Wind"
        elif 1 <= wind_speed < 16:
            return wind_stats[1] # Return "Slightly Windy"
        elif 16 <= wind_speed < 31:
            return wind_stats[2] # Return "Windy"
        elif 31 <= wind_speed < 51:
            return wind_stats[3] # Return "Very Windy"
        elif 51 <= wind_speed < 76:
            return wind_stats[4] # Return "Stormy"
        elif wind_speed >= 76:
            return wind_stats[5] # Return "Violent Storm"
        else:
            raise ValueError("Invalid wind speed value.") # If implemented correctly, this scenario should never occur
    elif units == "Imperial": # If the wind speed is in mph
        if 0 <= wind_speed < 1: # Wind speed between 0 mph (incl.) and 1 mph (excl.) and so on
            return wind_stats[0] # Return "No Wind"
        elif 1 <= wind_speed < 10:
            return wind_stats[1] # Return "Slightly Windy"
        elif 10 <= wind_speed < 19:
            return wind_stats[2] # Return "Windy"
        elif 19 <= wind_speed < 32:
            return wind_stats[3] # Return "Very Windy"
        elif 32 <= wind_speed < 46:
            return wind_stats[4] # Return "Stormy"
        elif wind_speed >= 46:
            return wind_stats[5] # Return "Violent Storm"
        else:
            raise ValueError("Invalid wind speed value.") # If implemented correctly, this scenario should never occur

def main():
    """
    The main function
    """
    app = Weather()
    app.win.mainloop() # Run the app

if __name__ == "__main__":
    main()