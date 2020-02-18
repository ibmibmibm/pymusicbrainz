from asyncio import get_running_loop, sleep
from threading import Lock
import httpx


class Request(object):
    def __init__(self, config, client):
        self.config = config
        self._client = client
        self._lock = Lock()
        self._rate_limit_time = None

    def get_url(self, path, **params):
        url = httpx.URL(
            "https://{host}:{port}/".format(
                host=self.config.server_host, port=self.config.server_port
            ),
            False,
            httpx.QueryParams(params),
        )
        url = url.join(path)
        return str(url)

    def get_headers(self):
        headers = {"User-Agent": self.config.user_agent}
        if self.config.access_token:
            headers["Authorization"] = "Bearer " + self.config.access_token
        return headers

    async def _ratelimit(self):
        while True:
            sleep_time = None
            with self._lock:
                now = get_running_loop().time()
                if self._rate_limit_time and now < self._rate_limit_time:
                    sleep_time = self._rate_limit_time - now
                else:
                    self._rate_limit_time = (
                        now + self.config.rate_limit_interval
                    )
            if sleep_time is None:
                return
            await sleep(sleep_time)

    async def get(self, path, **params):
        await self._ratelimit()
        return self._client.get(
            self.get_url(path), params=params, headers=self.get_headers(),
        )

    async def post(self, path, **params):
        await self._ratelimit()
        return self._client.post(
            self.get_url(path), data=params, headers=self.get_headers(),
        )

    async def get_stream(self, path, **params):
        await self._ratelimit()
        return self._client.stream(
            "GET",
            self.get_url(path),
            params=params,
            headers=self.get_headers(),
        )

    async def post_stream(self, path, **params):
        await self._ratelimit()
        return self._client.stream(
            "POST", self.get_url(path), data=params, headers=self.get_headers(),
        )
