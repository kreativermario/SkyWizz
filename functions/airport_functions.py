import requests
import os
from dotenv import load_dotenv

load_dotenv()

# IMPORT YOUR API KEY BEFORE EXECUTING FROM VENV OR JUST TYPE IT BELOW

API_KEY = os.getenv('API_KEY')


# API_KEY = "YOUR_API_KEY"  - uncomment this if you're not using venv

headers = {
		"X-RapidAPI-Key": API_KEY,
		"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
	}

# Functions that are called by the GUI
def airport_status(airport_code, code_type):
	"""
	:param airport_code: ICAO code of the airport
	:return:
	"""
	url = f"https://aerodatabox.p.rapidapi.com/airports/{code_type}/{airport_code}"

	querystring = {"withTime": "true"}
	response = requests.request("GET", url, headers=headers, params=querystring)

	# Check if the API response was sucessful
	if response.status_code != 200:
		raise Exception(f"API fetch failed! Status code: {response.status_code}")

	# Extract JSON
	try:
		json = response.json()
		icao_code = json["icao"]
		iata_code = json["iata"]
		full_name = json["fullName"]
		country_code = json["country"]["code"]
		country_name = json["country"]["name"]
		timezone = json["timeZone"]
	except (KeyError, json.JSONDecodeError):
		raise Exception("API response did not contain any data")

	text = f"Full Airport Name: {full_name}\n" \
		   f"Country Code: {country_code}\n" \
		   f"Country Name: {country_name}\n" \
		   f"IATA Code: {iata_code}\n" \
		   f"ICAO Code: {icao_code}\n" \
		   f"Timezone: {timezone}"

	return text


def check_airport_code(airport_code):
	# If it is IATA Code
	if len(airport_code) == 3:
		return "iata"
	# If it is ICAO Code
	elif len(airport_code) == 4:
		return "icao"
	else:
		return None

def distance_between_airports(airport1=None, airport2=None):
	if airport1 is None or airport2 is None:
		raise Exception("Airports can not be empty!")

	airport1 = check_airport_code(airport1)
	airport2 = check_airport_code(airport2)

	if airport1 is None or airport2 is None:
		raise Exception("Airports are not ICAO or IATA code")

	#url = f"https://aerodatabox.p.rapidapi.com/airports/{code_type}/{airport1}/distance-time/{airport2}"

