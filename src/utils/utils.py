def check_request_status(response):
    """
    Function that checks the API response status code
    :param response: API Response
    :return: Raises exceptions if the API request fails
    """
    if response.status_code != 200:
        raise Exception(f'API fetch failed! Status code: '
                        f'{response.status_code}')


def get_airport_code_type(airport_code):
    # If it is IATA Code
    if len(airport_code) == 3:
        return 'iata'
    # If it is ICAO Code
    elif len(airport_code) == 4:
        return 'icao'
    else:
        return None
