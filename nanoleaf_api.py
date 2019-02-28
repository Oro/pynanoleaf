import logging
import requests

logger = logging.getLogger(__name__)


class Nanoleaf(object):
    """Nanoleaf API wrapper"""
    def __init__(self, host, token, port=16021, protocol='http'):
        self.host = host
        self.token = token
        self.port = port
        self.protocol = protocol
        self._session = requests.Session()
        self.baseUrl = '{}://{}:{}/api/v1/'.format(
            self.protocol, self.host, self.port)
        self.authenticatedUrl = '{}{}'.format(self.baseUrl, self.token)

    def info(self):
        return self._request("/", 'GET').json()

    def add_user(self):
        return self._request("new", 'POST', authenticated=False).json()

    def _request(self, path, method=None, data=None, authenticated=True):
        if authenticated:
            url = self.authenticatedUrl + path
        else:
            url = self.baseUrl + path
        try:
            req = requests.Request(method, url, data=data)
            response = self._session.send(req.prepare())
            response.raise_for_status()
            logger.info("STATUS CODE {}".format(response.status_code))
            logger.info(response.json())
            return (response)
        except(requests.ConnectionError, requests.Timeout) as e:
            raise Unavailable("{} is not available".format(self.host)) from e
        except(requests.HTTPError) as e:
            if e.response.status_code == 400:
                raise NanoleafError("Bad Request sent") from e
            elif e.response.status_code == 401:
                raise InvalidToken("Invalid Token for {}"
                                   .format(self.host)) from e
            elif e.response.status_code == 403:
                raise NotAuthorizingNewTokens(
                    """Nanoleaf is not allowing new tokens,
                    please make sure to press and hold the on/off button
                    on your device for 5 seconds until the LED starts flashing
                    in a pattern.""") from e
            elif e.response.status_code == 404:
                raise Unavailable("{} is not existing".format(url)) from e
            else:
                raise NanoleafError("Unknown Error occured") from e


class NanoleafError(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)


class Unavailable(NanoleafError):
    pass


class NotAuthorizingNewTokens(NanoleafError):
    pass


class InvalidToken(NanoleafError):
    pass
