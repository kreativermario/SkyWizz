import requests

api_key = "YOUR_API_KEY" # Hide in venv
airport_code = "LAX"  # Replace with user input

url = f"https://api.openweathermap.org/data/2.5/weather?q={airport_code}&appid={api_key}&units=imperial"

response = requests.get(url)
data = response.json()

# Extract relevant weather data
temperature = data["main"]["temp"]
wind_speed = data["wind"]["speed"]
precipitation = data.get("rain", 0) + data.get("snow", 0)
