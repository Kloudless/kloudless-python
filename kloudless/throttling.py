import abc

from . import exceptions

class Throttling:
    __metaclass__ = abc.ABCMeta

    def __init__(self, max_retries=2):
        self.max_delay = 10
        self.counter = 0
        self.max_retries = max_retries

    def _header_check(self, response):
        if 'Retry-After' in response.headers:
            return float(response.headers['Retry-After'])

    def track(self, response):
        if response.status_code == 429:
            self.counter += 1
        else:
            self.counter = 0

        if self.counter > self.max_retries:
            self.counter = 0
            raise exceptions.RateLimitException(response=response)

    def track_and_delay(self, response):
        """
        Tracks a 429 and returns a delay if a retry is required.
        None if no retry required.
        Exception if too many retries.
        """
        self.track(response)

        delay = self._header_check(response)

        if not delay:
            delay = self._get_delay(response)

        if not delay:
            return

        return min(self.max_delay, delay)

    @abc.abstractmethod
    def _get_delay(self, response):
        raise NotImplementedError()

class ExpFallback(Throttling):
    def _get_delay(self, response):
        return max(0, int(2**(self.counter - 1)))

