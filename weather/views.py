import requests
from django.shortcuts import render
from django.core.cache import cache
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city):
    """
    Fetch weather data with caching
    """
    if not city:
        return {"error": "Please enter a city name."}

    city = city.strip().lower()

    # 🔥 Step 1: Check cache
    cached_data = cache.get(city)
    if cached_data:
        print("From Cache ⚡")
        return cached_data

    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        weather_data = {
            "city": data.get("name"),
            "temperature": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "description": data.get("weather", [{}])[0].get("description"),
            "icon": data.get("weather", [{}])[0].get("icon"),
        }

        # 🔥 Step 2: Store in cache (10 mins)
        cache.set(city, weather_data, timeout=600)

        print("From API 🌐")
        return weather_data

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}

    except requests.exceptions.HTTPError:
        return {"error": "City not found."}

    except Exception:
        return {"error": "Something went wrong."}


def index(request):
    """
    Main Django view
    """
    context = {}

    if request.method == "POST":
        city = request.POST.get("city", "").strip()

        weather_data = fetch_weather(city)
        context["weather"] = weather_data

    return render(request, "index.html", context)