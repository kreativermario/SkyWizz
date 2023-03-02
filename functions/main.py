import requests
import os
from dotenv import load_dotenv

load_dotenv()

# IMPORT YOUR API KEY BEFORE EXECUTING FROM VENV OR JUST TYPE IT BELOW

API_KEY = os.getenv('API_KEY')


# API_KEY = "YOUR_API_KEY"  - uncomment this if you're not using venv


# Functions that are called by the GUI
def airport_status(airport_code):
	"""
	:param airport_code: ICAO code of the airport
	:return:
	"""
	url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{airport_code}"

	querystring = {"withTime": "true"}

	headers = {
		"X-RapidAPI-Key": API_KEY,
		"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)
	return response.text
