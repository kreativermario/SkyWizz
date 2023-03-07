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


def check_request_status(response):
	"""
	Function that checks the API response status code
	:param response: API Response
	:return: Raises exceptions if the API request fails
	"""
	if response.status_code != 200:
		raise Exception(f"API fetch failed! Status code: {response.status_code}")


def get_airport_info(airport_code, code_type):
	"""
	:param airport_code: ICAO code of the airport
	:return:
	"""
	url = f"https://aerodatabox.p.rapidapi.com/airports/{code_type}/{airport_code}"

	querystring = {"withTime": "true"}
	response = requests.request("GET", url, headers=headers, params=querystring)

	# Check if the API response was sucessful
	check_request_status(response)

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
	"""
	Function that returns the distance in time between two airports
	:param airport1: First airport argument that must be either ICAO or IATA code
	:param airport2: Second airport argument that must be either ICAO or IATA code
	:return:
	"""
	# check if arguments are empty or not
	if airport1 is None or airport2 is None:
		raise Exception("Airports can not be empty!")
	else:
		code_type1 = check_airport_code(airport1)
		code_type2 = check_airport_code(airport2)

	if code_type1 is None or code_type2 is None:
		raise Exception("Airports are not ICAO or IATA code")
	elif code_type1 != code_type2:
		raise Exception("Airports are not in the same code format!")

	url = f"https://aerodatabox.p.rapidapi.com/airports/{code_type1}/{airport1}/distance-time/{airport2}"

	response = requests.request("GET", url, headers=headers)

	# Check if the API response was sucessful
	check_request_status(response)

	# Extract JSON
	try:
		json = response.json()
		icao_airport_1 = json["from"]["icao"]
		icao_airport_2 = json["to"]["icao"]
		name_airport_1 = json["from"]["name"]
		name_airport_2 = json["to"]["name"]
		distance_km = round(json["greatCircleDistance"]["km"],2)
		distance_time = json["approxFlightTime"]
	except (KeyError, json.JSONDecodeError):
		raise Exception("API response did not contain any data")

	text = f"------------------- CALCULATED DISTANCE BETWEEN -------------------\n " \
		   f"------------------- AIRPORTS ------------------- \n" \
		   f"{icao_airport_1} - {name_airport_1}\n" \
		   f"{icao_airport_2} - {name_airport_2} is:\n" \
		   f"------------------- DISTANCE IN KM ------------------- \n" \
		   f"{distance_km} \n" \
		   f"------------------- APPROXIMATE FLIGHT TIME ------------------- \n" \
		   f"{distance_time}"
	return text



