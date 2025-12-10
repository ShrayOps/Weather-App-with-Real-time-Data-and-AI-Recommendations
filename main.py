import customtkinter as ctk
import requests
from datetime import datetime
import pytz
from PIL import Image, ImageTk
import io
from CTkMessagebox import CTkMessagebox
from pathlib import Path
import google.generativeai as genai
import os

os.environ['TK_SILENCE_DEPRECATION'] = '1'

class WeatherApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Weather Dashboard")
        self.root.geometry("650x1050")  # Extended window height to accommodate all weather information
        
        # Initialize application theme settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize API authentication credentials
        self.weather_api_key = "<API KEY GOES HERE>"
        self.aqi_api_key = "<API KEY GOES HERE>"
        
        # Initialize Gemini API configuration
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Directory path configuration for application icons
        self.icons_dir = Path("/Users/shreyash/Desktop/Study/Subjects/Python/Integrated Project/abcpng")
        self.icons = {
            "search": self.load_icon("search.png"),
            "thermometer": self.load_icon("thermometer.png"),
            "droplets": self.load_icon("droplets.png"),
            "wind": self.load_icon("wind.png"),
            "leaf": self.load_icon("leaf.png"),
            "map-pin": self.load_icon("map-pin.png"),
            "clock": self.load_icon("clock.png"),
            "sunrise": self.load_icon("sunrise.png"),
            "sunset": self.load_icon("sunset.png"),
            "pressure": self.load_icon("gauge.png"),
            "humidity": self.load_icon("droplets.png")
        }
        
        self.setup_gui()
        self.get_weather("Delhi")  # default location

    def load_icon(self, icon_name):
        """
        Loads and processes icon images for the application interface
        
        Parameters:
            icon_name (str): Filename of the icon to be loaded
            
        Returns:
            PhotoImage: Processed icon image ready for display
        """
        icon_path = self.icons_dir / icon_name
        try:
            with Image.open(icon_path) as img:
                img = img.convert('RGBA')
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Icon loading error - {icon_name}: {e}")
            return None

    def setup_gui(self):
        # Primary application container implementation
        main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=20
        )
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Search functionality implementation
        search_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=15
        )
        search_frame.pack(padx=15, pady=15, fill="x")
        
        self.city_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter city name...",
            height=45,
            font=("Inter", 16),
            corner_radius=12,
            border_width=0
        )
        self.city_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        search_button = ctk.CTkButton(
            search_frame,
            image=self.icons["search"],
            text="",
            width=45,
            height=45,
            corner_radius=12,
            command=self.get_weather
        )
        search_button.pack(side="right", padx=10)
        
        # Weather information display section
        self.weather_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        self.weather_frame.pack(padx=15, pady=10, fill="both", expand=True)
        
        # Location and temporal information display
        location_frame = ctk.CTkFrame(
            self.weather_frame,
            corner_radius=15
        )
        location_frame.pack(pady=10, fill="x")
        
        self.city_label = ctk.CTkLabel(
            location_frame,
            text="",
            font=("Inter", 28, "bold"),
            anchor="w"
        )
        self.city_label.pack(padx=15, pady=(10,0))
        
        self.time_label = ctk.CTkLabel(
            location_frame,
            text="",
            font=("Inter", 16),
            text_color="gray60",
            anchor="w"
        )
        self.time_label.pack(padx=15, pady=(0,10))
        
        # Temperature and weather condition visualization
        temp_frame = ctk.CTkFrame(
            self.weather_frame,
            corner_radius=15
        )
        temp_frame.pack(pady=10, fill="x")
        
        self.temp_label = ctk.CTkLabel(
            temp_frame,
            text="",
            font=("Inter", 64, "bold")
        )
        self.temp_label.pack(pady=(10,0))
        
        self.feels_like_label = ctk.CTkLabel(
            temp_frame,
            text="",
            font=("Inter", 16),
            text_color="gray60"
        )
        self.feels_like_label.pack(pady=(0,10))
        
        self.icon_label = ctk.CTkLabel(temp_frame, text="")
        self.icon_label.pack()
        
        self.desc_label = ctk.CTkLabel(
            temp_frame,
            text="",
            font=("Inter", 18)
        )
        self.desc_label.pack(pady=10)
        
        # Weather metrics grid implementation
        details_frame = ctk.CTkFrame(
            self.weather_frame,
            fg_color="transparent"
        )
        details_frame.pack(pady=10, fill="both")
        
        # Configure grid layout parameters
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Implementation of individual weather metric displays
        self.humidity_label = self.create_detail_card(details_frame, "humidity", " Humidity", "", 0, 0)
        self.wind_speed_label = self.create_detail_card(details_frame, "wind", " Wind Speed", "", 0, 1)
        self.air_quality_label = self.create_detail_card(details_frame, "leaf", " Air Quality", "", 1, 0)
        self.pressure_label = self.create_detail_card(details_frame, "pressure", " Pressure", "", 1, 1)
        
        # Solar event timing display implementation
        sun_frame = ctk.CTkFrame(
            self.weather_frame,
            corner_radius=15
        )
        sun_frame.pack(pady=10, fill="x")
        
        # Sunrise information display
        sunrise_frame = ctk.CTkFrame(sun_frame, fg_color="transparent")
        sunrise_frame.pack(side="left", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            sunrise_frame,
            image=self.icons["sunrise"],
            text=" Sunrise",
            compound="left",
            font=("Inter", 14)
        ).pack()
        
        self.sunrise_label = ctk.CTkLabel(
            sunrise_frame,
            text="",
            font=("Inter", 16, "bold")
        )
        self.sunrise_label.pack()
        
        # Sunset information display
        sunset_frame = ctk.CTkFrame(sun_frame, fg_color="transparent")
        sunset_frame.pack(side="right", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            sunset_frame,
            image=self.icons["sunset"],
            text=" Sunset",
            compound="left",
            font=("Inter", 14)
        ).pack()
        
        self.sunset_label = ctk.CTkLabel(
            sunset_frame,
            text="",
            font=("Inter", 16, "bold")
        )
        self.sunset_label.pack()

        # Weather recommendation system implementation
        ai_frame = ctk.CTkFrame(
            self.weather_frame,
            corner_radius=15
        )
        ai_frame.pack(pady=10, fill="x", padx=15)

        self.ai_recommendation_label = ctk.CTkLabel(
            ai_frame,
            text="",
            font=("Inter", 14),
            wraplength=485,
            justify="center",
            anchor="center"
        )
        self.ai_recommendation_label.pack(pady=10, padx=10, fill="x")

    def create_detail_card(self, parent, icon_key, title, value, row, col):
        """
        Creates standardized weather metric display cards
        
        Parameters:
            parent: Parent widget
            icon_key (str): Icon identifier
            title (str): Metric title
            value (str): Initial metric value
            row (int): Grid row position
            col (int): Grid column position
            
        Returns:
            CTkLabel: Configured value display label
        """
        card = ctk.CTkFrame(
            parent,
            corner_radius=15
        )
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            card,
            image=self.icons.get(icon_key),
            text=title,
            compound="left",
            font=("Inter", 14)
        ).pack(pady=(10,5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Inter", 20, "bold")
        )
        value_label.pack(pady=(0,10))
        
        return value_label

    def get_weather(self, city=None):
        """
        Retrieves weather data for specified location
        
        Parameters:
            city (str, optional): Target city name. Defaults to entry field value.
        """
        if city is None:
            city = self.city_entry.get()
        if not city:
            CTkMessagebox(
                title="Error",
                message="Please enter a city name",
                icon="warning"
            )
            self.root.focus_force()
            return

        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
        try:
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            if weather_data["cod"] != 200:
                CTkMessagebox(
                    title="Error",
                    message="City Not Found",
                    icon="warning"
                )
                self.city_entry.delete(0, 'end')
                self.root.focus_force()
                return

            lat = weather_data["coord"]["lat"]
            lon = weather_data["coord"]["lon"]

            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.aqi_api_key}"
            aqi_response = requests.get(aqi_url)
            aqi_data = aqi_response.json()

            self.update_weather_display(weather_data, aqi_data)

        except requests.RequestException:
            CTkMessagebox(
                title="Error",
                message="Failed to fetch weather data",
                icon="cancel"
            )
            self.city_entry.delete(0, 'end')
            self.root.focus_force()

    def update_weather_display(self, weather_data, aqi_data):
        """
        Updates interface with retrieved weather information
        
        Parameters:
            weather_data (dict): Weather information from API
            aqi_data (dict): Air quality information from API
        """
        # Update location and time information
        self.city_label.configure(text=weather_data["name"])
        
        timezone_offset = weather_data["timezone"]
        local_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
        local_time = local_time.astimezone(pytz.FixedOffset(timezone_offset//60))
        self.time_label.configure(text=local_time.strftime("%I:%M %p, %A"))

        # Update temperature information
        temp = round(weather_data["main"]["temp"])
        feels_like = round(weather_data["main"]["feels_like"])
        self.temp_label.configure(text=f"{temp}°C")
        self.feels_like_label.configure(text=f"Feels like {feels_like}°C")
        
        description = weather_data["weather"][0]["description"].capitalize()
        self.desc_label.configure(text=description)

        # Update atmospheric metrics
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        pressure = weather_data["main"]["pressure"]
        
        self.humidity_label.configure(text=f"{humidity}%")
        self.wind_speed_label.configure(text=f"{wind_speed} m/s")
        self.pressure_label.configure(text=f"{pressure} hPa")

        aqi = aqi_data["list"][0]["main"]["aqi"]
        aqi_text = ["", "Good", "Fair", "Moderate", "Poor", "Very Poor"][aqi]
        self.air_quality_label.configure(text=aqi_text)

        # Update solar event timings
        sunrise_time = datetime.fromtimestamp(weather_data["sys"]["sunrise"])
        sunset_time = datetime.fromtimestamp(weather_data["sys"]["sunset"])
        
        self.sunrise_label.configure(text=sunrise_time.strftime("%I:%M %p"))
        self.sunset_label.configure(text=sunset_time.strftime("%I:%M %p"))

        # Update weather condition icon
        icon_code = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            icon_response = requests.get(icon_url)
            icon_image = Image.open(io.BytesIO(icon_response.content))
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.icon_label.configure(image=icon_photo)
            self.icon_label.image = icon_photo
        except:
            self.icon_label.configure(image="")

        # Generate weather-based recommendations
        self.generate_ai_recommendation(weather_data, aqi_data)

    def generate_ai_recommendation(self, weather_data, aqi_data):
        """
        Generates contextual weather recommendations
        
        Parameters:
            weather_data (dict): Current weather conditions
            aqi_data (dict): Current air quality metrics
        """
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        description = weather_data["weather"][0]["description"]
        aqi = aqi_data["list"][0]["main"]["aqi"]

        prompt = f"""
        Given the following weather conditions:
        - Temperature: {temp}°C
        - Feels Like: {feels_like}°C
        - Humidity: {humidity}%
        - Wind Speed: {wind_speed} m/s
        - Weather Description: {description}
        - Air Quality Index: {aqi}

        Provide a one line recommendation (no more than 13 words) for activities or precautions 
        based on these weather conditions. The recommendation should be 
        concise, and directly related to the current weather.
        """

        response = self.model.generate_content(prompt)
        recommendation = response.text.strip()

        formatted_recommendation = f"{recommendation}"

        self.ai_recommendation_label.configure(text=formatted_recommendation)

if __name__ == "__main__":
    os.environ['GOOGLE_API_KEY'] = '<API KEY GOES HERE>'
    app = WeatherApp()
    app.root.mainloop()
