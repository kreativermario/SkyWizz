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
    """
    Function that returns which airport code type
    :param airport_code: Airport set of code
    :return: code: type of airport code
    :rtype: code: str
    """
    code = None
    # If it is IATA Code
    if len(airport_code) == 3:
        code = 'iata'
    # If it is ICAO Code
    elif len(airport_code) == 4:
        code = 'icao'
    return code


def validate_airport_code(airport_code):
    """
    Functions that validades airport code
    :param airport_code: The airport code
    :type airport_code: str
    :return:
    """
    if airport_code is None:
        raise Exception("Airport code is not valid! Try using IATA or "
                        "ICAO code format")
