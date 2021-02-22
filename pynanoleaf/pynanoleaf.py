import logging
import requests

logger = logging.getLogger(__name__)


def _deepgetter(key):
    """Retrieve value from nested dicts"""
    def get(data):
        for k in key:
            data = data[k]
        if ('.'.join(key) == 'effects.select'):
            return _parseEffect(data)
        return data
    return get


def _deepsetter(key):
    """Set value in nested dicts"""
    def set(data, value):
        # Fill structure with empty dictionaries up to but not including the
        # final key part.
        for k in key[:-1]:
            data = data.setdefault(k, {})
        data[key[-1]] = value
    return set


def _dictitem_property(keystr):
    """Property backed by nested dict items"""
    key = keystr.split('.')
    return property(
        fget=_deepgetter(key),
        fset=_deepsetter(key)
    )

def _parseEffect(effect):
    """These effect names have special meaning and are not directly setable
    and should not be returned as effect name for Consumers."""
    RESERVED_EFFECT_NAMES = ["*Solid*", "*Static*", "*Dynamic*"]
    try:
        RESERVED_EFFECT_NAMES.index(effect)
        return None
    except ValueError:
        return effect


class _Info(dict):
    """General info about the Nanoleaf"""

    serialNo = _dictitem_property('serialNo')
    firmwareVersion = _dictitem_property('firmwareVersion')
    model = _dictitem_property('model')
    name = _dictitem_property('name')
    manufacturer = _dictitem_property('manufacturer')
    hardwareVersion = _dictitem_property('hardwareVersion')
    effects = _dictitem_property('effects.effectsList')
    effectSelect = _dictitem_property('effects.select')


class _State(dict):
    """State of the Nanoleaf"""

    on = _dictitem_property('on.value')
    brightness = _dictitem_property('brightness.value')
    min_brightness = _dictitem_property('brightness.min')
    max_brightness = _dictitem_property('brightness.max')
    hue = _dictitem_property('hue.value')
    min_hue = _dictitem_property('hue.min')
    max_hue = _dictitem_property('hue.max')
    saturation = _dictitem_property('sat.value')
    min_saturation = _dictitem_property('sat.min')
    max_saturation = _dictitem_property('sat.max')
    color_temperature = _dictitem_property('ct.value')
    min_color_temperature = _dictitem_property('ct.min')
    max_color_temperature = _dictitem_property('ct.max')
    color_mode = _dictitem_property('colorMode')

    def __init__(self, data=None, **kwargs):
        super().__init__(data or {})
        for key, value in kwargs.items():
            setattr(self, key, value)


class Nanoleaf(object):
    """Nanoleaf API wrapper"""

    Info = _Info
    State = _State

    def __init__(self, host, token=None, port=16021, protocol='http',
                 timeout=2):
        self.host = host
        self.token = token
        self.port = port
        self.protocol = protocol
        self._session = requests.Session()
        self.timeout = timeout

    @property
    def baseUrl(self):
        return '{}://{}:{}/api/v1/'.format(
            self.protocol, self.host, self.port)

    @property
    def authenticatedUrl(self):
        return '{}{}/'.format(self.baseUrl, self.token)

    @property
    def available(self):
        "Returns True if the Nanoleaf device is available"
        try:
            self.info
        except Exception:
            return False
        return True

    @property
    def info(self) -> Info:
        return self.Info(self._get("/"))

    @property
    def state(self) -> State:
        return self.State(self._get("state"))

    @state.setter
    def state(self, state: State) -> None:
        self._put("state", state)

    def update(self, **kwargs) -> None:
        self._put("state", self.State(**kwargs))

    @property
    def serialNo(self):
        return self._get("/")['serialNo']

    @property
    def firmwareVersion(self):
        return self._get("/")["firmwareVersion"]

    @property
    def model(self):
        return self._get("/")['model']

    @property
    def name(self):
        return self._get("/")['name']

    def request_token(self):
        """Returns a new token from the Nanoleaf device.
        If you want this token to be used in new requests use
        the authenticate() method instead.
        This only works when the on/off button on the device
        is helt for 5-7 seconds and the LED starts flashing.

        Will raise a NotAuthorizingNewTokens Exception otherwise"""
        response = self._request("new", 'POST', authenticated=False).json()
        return response['auth_token']

    def authorize(self):
        """Requests a new token from the Nanoleaf device
        and sets it as the currently used one. If you just want to request a
        new token use the request_token method instead.
        This only works when the on/off button on the device
        is helt for 5-7 seconds and the LED starts flashing.

        Will raise a NotAuthorizingNewTokens Exception otherwise"""
        self.token = self.request_token()

    def delete_token(self):
        """Deletes the currently used token. This is not reversible.
        You will have to request a new token if you want to use the
        Nanoleaf integration with that device."""
        return self._request("/", 'DELETE')

    @property
    def on(self):
        return self._get("state/on")['value']

    @on.setter
    def on(self, value: bool):
        self._put("state", {"on": {"value": value}})

    @property
    def off(self):
        return self._get("state/on")['value']

    @off.setter
    def off(self, value: bool):
        self._put("state", {"on": {"value": not value}})

    @property
    def brightness(self):
        return self._get("state/brightness")['value']

    @property
    def max_brightness(self):
        return self._get("state/brightness")['max']

    @property
    def min_brightness(self):
        return self._get("state/brightness")['min']

    @brightness.setter
    def brightness(self, value: int):
        self._put("state", {"brightness": {"value": value}})

    def brightness_transition(self, value: int, duration: int):
        """Sets the brightness to the specified value
        with a transition lastind duration seconds"""
        self._put("state/brightness",
                  {"brightness": {"value": value, "duration": duration}})

    @property
    def hue(self):
        return self._get("state/hue")['value']

    @property
    def max_hue(self):
        return self._get("state/hue")['max']

    @property
    def min_hue(self):
        return self._get("state/hue")['min']

    @hue.setter
    def hue(self, value: int):
        self._put("state", {"hue": {"value": value}})

    @property
    def saturation(self):
        return self._get("state/sat")['value']

    @property
    def max_saturation(self):
        return self._get("state/sat")['max']

    @property
    def min_saturation(self):
        return self._get("state/sat")['min']

    @saturation.setter
    def saturation(self, value: int):
        self._put("state", {"sat": {"value": value}})

    @property
    def color_temperature(self):
        return self._get("state/ct")['value']

    @property
    def max_color_temperature(self):
        return self._get("state/ct")['max']

    @property
    def min_color_temperature(self):
        return self._get("state/ct")['min']

    @color_temperature.setter
    def color_temperature(self, value: int):
        self._put("state", {"ct": {"value": value}})

    @property
    def color_mode(self):
        return self._get("state/colorMode")['value']

    @property
    def effect(self):
        return _parseEffect(self._get("effects/select"))

    @effect.setter
    def effect(self, value):
        self._put("effects", {"select": value})

    @property
    def effects(self):
        return self._get("effects/effectsList")

    def _request(self, path, method=None, data=None, authenticated=True):
        if authenticated:
            url = self.authenticatedUrl + path
        else:
            url = self.baseUrl + path
        try:
            req = requests.Request(method, url, json=data)
            response = self._session.send(req.prepare(), timeout=self.timeout)
            response.raise_for_status()
            if response.status_code == 200:
                logger.debug(response.json())
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
                raise Unavailable("{} returns 404".format(url)) from e
            else:
                raise NanoleafError("Unknown Error occured") from e

    def _get(self, path, key=None):
        "Helper method to GET a URL"
        response = self._request(path, 'GET').json()
        return response

    def _put(self, path, data):
        "Helper method to PUT data at an URL"
        self._request(path, 'PUT', data)


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
