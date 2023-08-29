class AirportCodeError(Exception):
    """Base class for exceptions related to airport codes"""
    pass


class EmptyAirportCodeError(AirportCodeError):
    """Raised when the airport code argument is empty"""
    pass


class InvalidAirportCodeError(AirportCodeError):
    """Raised when the airport code is not a valid IATA or ICAO code"""
    pass


class DifferentCodeFormatError(AirportCodeError):
    """Raised when the two airport codes are not in the same format"""
    pass


class APIDataError(Exception):
    """Base class for exceptions related to API data"""
    pass


class EmptyAPIResponseError(APIDataError):
    """Raised when the API response did not contain any data"""
    pass


class APIRequestError(APIDataError):
    """Raised when there was an error with the API request"""
    pass
