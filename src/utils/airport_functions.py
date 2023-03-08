import json
import requests
import os
from dotenv import load_dotenv
from src.utils.utils import get_airport_code_type, check_request_status


load_dotenv()

# IMPORT YOUR API KEY BEFORE EXECUTING FROM VENV OR JUST TYPE IT BELOW

API_KEY = os.getenv('API_KEY')

# API_KEY = 'YOUR_API_KEY'  - uncomment this if you're not using venv

headers = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': 'aerodatabox.p.rapidapi.com'
}


def get_airport_info(airport_code, code_type):
    """
    :param airport_code: ICAO code of the airport
    :return:
    """
    url = f'https://aerodatabox.p.rapidapi.com/airports/' \
          f'{code_type}/{airport_code}'

    querystring = {'withTime': 'true'}
    response = requests.request('GET', url, headers=headers,
                                params=querystring)

    # Check if the API response was sucessful
    check_request_status(response)

    # Extract JSON
    try:
        airport_data = response.json()
        icao_code = airport_data['icao']
        iata_code = airport_data['iata']
        full_name = airport_data['fullName']
        country_code = airport_data['country']['code']
        country_name = airport_data['country']['name']
        timezone = airport_data['timeZone']
    except (KeyError, json.JSONDecodeError):
        raise Exception('API response did not contain any data')

    text = f'Full Airport Name: {full_name}\n' \
           f'Country Code: {country_code}\n' \
           f'Country Name: {country_name}\n' \
           f'IATA Code: {iata_code}\n' \
           f'ICAO Code: {icao_code}\n' \
           f'Timezone: {timezone}'

    return text


def distance_between_airports(airport1=None, airport2=None):
    """
    Function that returns the distance in time between two airports
    :param airport1: First airport argument that must be either ICAO or
                                                                IATA code
    :param airport2: Second airport argument that must be either ICAO or
                                                                IATA code
    :return:
    """
    # check if arguments are empty or not
    if airport1 is None or airport2 is None:
        raise Exception('Airports can not be empty!')
    else:
        code_type1 = get_airport_code_type(airport1)
        code_type2 = get_airport_code_type(airport2)

    if code_type1 is None or code_type2 is None:
        raise Exception('Airports are not ICAO or IATA code')
    elif code_type1 != code_type2:
        raise Exception('Airports are not in the same code format!')

    url = f'https://aerodatabox.p.rapidapi.com/airports/{code_type1}' \
          f'/{airport1}/distance-time/{airport2}'

    response = requests.request('GET', url, headers=headers)

    # Check if the API response was sucessful
    check_request_status(response)

    # Extract JSON
    try:
        json = response.json()
        icao_airport_1 = json['from']['icao']
        icao_airport_2 = json['to']['icao']
        name_airport_1 = json['from']['name']
        name_airport_2 = json['to']['name']
        distance_km = round(json['greatCircleDistance']['km'], 2)
        distance_time = json['approxFlightTime']
    except (KeyError, json.JSONDecodeError):
        raise Exception('API response did not contain any data')

    text = f'------------------- ' \
           f'CALCULATED DISTANCE BETWEEN ' \
           f'-------------------\n ' \
           f'------------------- ' \
           f'AIRPORTS' \
           f' ------------------- \n' \
           f'{icao_airport_1} - {name_airport_1}\n' \
           f'{icao_airport_2} - {name_airport_2} is:\n' \
           f'------------------- ' \
           f'DISTANCE IN KM ' \
           f'------------------- \n' \
           f'{distance_km} \n' \
           f'------------------- ' \
           f'APPROXIMATE FLIGHT TIME' \
           f' ------------------- \n' \
           f'{distance_time}'
    return text
