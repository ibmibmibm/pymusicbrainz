from .config import Config
from .oauth import OAuth
from .model import (
    Parser,
    Area,
    Artist,
    Collection,
    Event,
    Instrument,
    Label,
    Place,
    Recording,
    Release,
    ReleaseGroup,
    Series,
    Work,
    Url,
)

import re
import functools
import asyncio
from collections import defaultdict
from logging import getLogger

import httpx
from lxml import etree

log = getLogger(__name__)

uuid_regex = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)

valid_scope = {
    "profile",
    "email",
    "tag",
    "rating",
    "collection",
    "submit_isrc",
    "submit_barcode",
}

class AsyncSession(object):
    def __init__(self, config=None, scopes=None, *args, **kwargs):
        if config is None:
            config = Config()
        if scopes is None:
            scopes = []

        for scope in scopes:
            if scope not in valid_scope:
                raise ValueError(f"invalid scope {scope}!")

        self.config = config
        self._oauth = OAuth(
            config, httpx.AsyncClient(http2=True, *args, **kwargs)
        )
        self.scopes = scopes

    def get_authorization_url(self):
        return self._oauth.get_authorization_url(self.scopes)

    async def exchange_authorization_code(self, token):
        await self._oauth.exchange_authorization_code(token, self.scopes)

    async def _get_stream(self, path, inc):
        parser = etree.XMLParser(target=Parser())
        async with await self._oauth.get_stream(path, inc=" ".join(inc)) as r:
            async for chunk in r.aiter_bytes():
                yield chunk

    async def _get_xml(self, path, inc):
        parser = etree.XMLParser(target=Parser())
        async for chunk in self._get_stream(path, inc):
            parser.feed(chunk)
        return parser.close()

    async def _load_xml(self, file_path):
        parser = etree.XMLParser(target=Parser())
        with open(file_path, "rb") as fp:
            for chunk in iter(functools.partial(fp.read, 4096), b''):
                parser.feed(chunk)
        return parser.close()

    @staticmethod
    def _check_valid_id(id):
        if uuid_regex.match(id) is None:
            raise ValueError(f"Invalid id {id}")

    @staticmethod
    def _check_login_required(inc):
        if inc.startswith("user-") and not self._oauth.is_logged_in():
            raise ValueError(f"Invalid id {id}")

    async def _lookup(self, id, includes, cls, name):
        if includes is None:
            includes = []
        self._check_valid_id(id)
        for inc in includes:
            self._check_login_required(inc)
            if cls.valid_lookup_include(inc):
                continue
            raise ValueError(f"invalid include {inc}")
        metadata = await self._get_xml(f"/ws/2/{name}/{id}", includes)
        return metadata[name]

    async def lookup_artist(self, id, includes=None):
        self._check_valid_id(id)
        if includes is None:
            includes = []
        has_release = "releases" in includes
        for inc in includes:
            self._check_login_required(inc)
            if Artist.valid_lookup_include(inc):
                continue
            if has_release:
                if inc == "various-artists":
                    continue
            raise ValueError(f"invalid include {inc}")

        metadata = await self._get_xml(f"/ws/2/artist/{id}", includes)
        return metadata["artist"]

    async def lookup_area(self, id, includes=None):
        return await self._lookup(id, includes, Area, 'area')

    async def lookup_event(self, id, includes=None):
        return await self._lookup(id, includes, Event, 'event')

    async def lookup_instrument(self, id, includes=None):
        return await self._lookup(id, includes, Instrument, 'instrument')

    async def lookup_label(self, id, includes=None):
        return await self._lookup(id, includes, Label, 'label')

    async def lookup_place(self, id, includes=None):
        return await self._lookup(id, includes, Place, 'place')

    async def lookup_recording(self, id, includes=None):
        return await self._lookup(id, includes, Recording, 'recording')

    async def lookup_release(self, id, includes=None):
        return await self._lookup(id, includes, Release, 'release')

    async def lookup_release_group(self, id, includes=None):
        return await self._lookup(id, includes, ReleaseGroup, 'release-group')

    async def lookup_series(self, id, includes=None):
        return await self._lookup(id, includes, Series, 'series')

    async def lookup_url(self, id, includes=None):
        return await self._lookup(id, includes, Url, 'url')

    async def lookup_work(self, id, includes=None):
        return await self._lookup(id, includes, Work, 'work')

    async def __aenter__(self) -> "AsyncSession":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._oauth._client.aclose()


class Session(AsyncSession):
    def __init__(self, *args, **kwargs):
        if asyncio.events._get_running_loop() is not None:
            raise RuntimeError(
                "Session cannot be construct from a running event loop"
            )
        super().__init__(*args, **kwargs)
        loop = asyncio.events.new_event_loop()
        asyncio.events.set_event_loop(loop)
        self._loop = loop

    def _await(self, main):
        return self._loop.run_until_complete(main)

    def exchange_authorization_code(self, *args, **kwargs):
        return self._await(super().exchange_authorization_code(*args, **kwargs))

    def lookup_artist(self, *args, **kwargs):
        return self._await(super().lookup_artist(*args, **kwargs))

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._await(self._oauth._client.aclose())
        loop = self._loop
        try:
            to_cancel = asyncio.tasks.all_tasks(loop)
            if to_cancel:
                for task in to_cancel:
                    task.cancel()
                loop.run_until_complete(
                    asyncio.tasks.gather(
                        *to_cancel, loop=loop, return_exceptions=True
                    )
                )

                for task in to_cancel:
                    if task.cancelled():
                        continue
                    if task.exception() is not None:
                        loop.call_exception_handler(
                            {
                                "message": "unhandled exception during asyncio.run() shutdown",
                                "exception": task.exception(),
                                "task": task,
                            }
                        )

            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.events.set_event_loop(None)
            loop.close()
