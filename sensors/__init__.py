import random
import requests
from typing import Self

from core.classes import Measurement, Metric, SensorBase, SensorDef, SettingsBase, Status
from core.config import ReadDict
from core.util import cast


class RandomSettings(SettingsBase):
    """
    Configuration for the sensor
    """
    @classmethod
    def deserialize(cls, conf: ReadDict) -> Self:
        # Python boolean expressions that will be evaluated
        unhealthy = conf['unhealthy'].as_str()
        degraded = conf['degraded'].as_str()

        # Optional static massage to add to the measurement
        message = conf['message'].as_str(None)

        return cls(unhealthy, degraded, message)
    
    def __init__(self, unhealthy: str, degraded: str, message: str | None) -> None:
        self.unhealthy = unhealthy
        self.degraded = degraded
        self.message = message

class RandomSensor(SensorBase[RandomSettings]):
    """
    A sensor that returns a problem *sometimes*,
    but that *sometimes* is configurable
    """
    def __init__(self, settings: RandomSettings) -> None:
        self.settings = settings

    def measure(self) -> Measurement:
        # Roll a random value to pass to expressions
        value = random.randrange(1, 100)

        # Set variables to be used in expressions
        context = {'value': value}

        # Evaluate expression
        xunhealthy = eval(self.settings.unhealthy, context)
        xdegraded = eval(self.settings.degraded, context)

        # Assert that the expression result is a bool
        unhealthy = cast('unhealthy()', xunhealthy, bool)
        degraded = cast('degraded()', xdegraded, bool)

        # Set measurement status according to expression result
        if unhealthy:
            status = Status.UNHEALTHY
        elif degraded:
            status = Status.DEGRADED
        else:
            status = Status.HEALTHY

        metrics = [
            # Attach the random value to the measurement
            Metric('random', 'integer', value),
        ]

        # Attach the custom message if set
        if self.settings.message is not None:
            metrics.append(Metric('message', 'string', self.settings.message))

        # Create a new measurement with current timestamp
        return Measurement.now(status, metrics)
    

class HTTPRequestSettings(SettingsBase):
    """
    Configuration for the sensor
    """
    @classmethod
    def deserialize(cls, conf: ReadDict) -> Self:
        # Target URL
        url = conf['url'].as_str()

        return cls(url)
    
    def __init__(self, url: str) -> None:
        self.url = url

class HTTPRequestSensor(SensorBase[HTTPRequestSettings]):
    """
    A sensor that performs an http request and returns the result
    """
    def __init__(self, settings: HTTPRequestSettings) -> None:
        self.settings = settings

    def measure(self) -> Measurement:
        # Perform HTTP request
        response = requests.get(self.settings.url)
        code = response.status_code
        text = response.text

        # Set measurement status based on return code
        if code in range(200, 300):
            status = Status.HEALTHY
        elif code in range(300, 400):
            status = Status.DEGRADED
        elif code in range(400, 600):
            status = Status.UNHEALTHY
        else:
            status = Status.UNKNOWN

        metrics = [
            # Attach the URL which was requested
            Metric('url', 'url', self.settings.url),
            # Attach HTTP status code
            Metric('code', 'integer', code),
            # Attach the response as text
            Metric('response', 'string', text),
        ]

        # Create a new measurement with current timestamp
        return Measurement.now(status, metrics)

# Register the sensors
SENSORS = [
    # This sensor can be used as example:random
    SensorDef('random', RandomSensor, RandomSettings),
    # This sensor can be used as example:http-request
    SensorDef('http-request', HTTPRequestSensor, HTTPRequestSettings),
]
