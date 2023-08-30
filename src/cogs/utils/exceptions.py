class APIDataError(Exception):
    """Base class for exceptions related to API data"""
    pass


class EmptyAPIResponseError(APIDataError):
    """Raised when the API response did not contain any data"""
    pass


class APIRequestError(APIDataError):
    """Raised when there was an error with the API request"""
    pass
