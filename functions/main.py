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
		iata_code = json["iata"]
		full_name = json["fullName"]
	except (KeyError, json.JSONDecodeError):
		raise Exception("API response did not contain any data")

	text = f"IATA Code: {iata_code}\nFull Airport Name: {full_name}"

	return text
