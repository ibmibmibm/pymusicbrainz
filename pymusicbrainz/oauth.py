from .const import (
    MUSICBRAINZ_OAUTH_CLIENT_ID,
    MUSICBRAINZ_OAUTH_CLIENT_SECRET,
)
from .request import Request
import time
from logging import getLogger
import httpx

log = getLogger(__name__)


class OAuth(Request):
    def __init__(self, config, client):
        super().__init__(config, client)
        self.config = config

    def is_authorized(self):
        return bool(
            self.config.refresh_token and self.config.refresh_token_scopes
        )

    def is_logged_in(self):
        return self.is_authorized() and bool(self.config.username)

    def forget_refresh_token(self):
        del self.config.refresh_token
        del self.config.refresh_token_scopes

    def forget_access_token(self):
        del self.config.access_token
        del self.config.access_token_expires

    async def get_access_token(self):
        if not self.is_authorized():
            return None
        if (
            not self.config.access_token
            or time.time() >= self.config.access_token_expires
        ):
            self.forget_access_token()
            await self.refresh_access_token()
        return self.config.access_token

    def get_authorization_url(self, scopes):
        return self.get_url(
            path="/oauth2/authorize",
            response_type="code",
            client_id=MUSICBRAINZ_OAUTH_CLIENT_ID,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            scope=" ".join(scopes),
        )

    def set_refresh_token(self, refresh_token, scopes):
        log.debug("got refresh_token %s with scopes %s", refresh_token, scopes)
        self.config.refresh_token = refresh_token
        self.config.refresh_token_scopes = scopes

    def set_access_token(self, access_token, expires_in):
        log.debug(
            "got access_token %s that expires in %s seconds",
            access_token,
            expires_in,
        )
        self.config.access_token = access_token
        self.config.access_token_expires = int(time.time() + expires_in - 60)

    async def refresh_access_token(self):
        log.debug(
            "refreshing access_token with a refresh_token %s",
            self.config.refresh_token,
        )
        try:
            async with await self.post(
                path="/oauth2/token",
                grant_type="refresh_token",
                refresh_token=self.config.refresh_token,
                client_id=MUSICBRAINZ_OAUTH_CLIENT_ID,
                client_secret=MUSICBRAINZ_OAUTH_CLIENT_SECRET,
            ) as r:
                status = r.status
                if status == 200 or status == 400:
                    data = r.json()

            if status == 200:
                self.set_access_token(data["access_token"], data["expires_in"])
                return access_token
            if status == 400:
                if data["error"] == "invalid_grant":
                    self.forget_refresh_token()
        except Exception as err:
            log.error("access_token refresh failed", exc_info=err)
        return None

    async def exchange_authorization_code(self, authorization_code, scopes):
        log.error(
            "exchanging authorization_code %s for an access_token",
            authorization_code,
        )
        try:
            async with await self.post(
                path="/oauth2/token",
                grant_type="authorization_code",
                code=authorization_code,
                client_id=MUSICBRAINZ_OAUTH_CLIENT_ID,
                client_secret=MUSICBRAINZ_OAUTH_CLIENT_SECRET,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            ) as r:
                await r.aread()
                data = r.json()
            if "error" in data:
                log.error("%s", data)
                return False
            self.set_refresh_token(data["refresh_token"], scopes)
            self.set_access_token(data["access_token"], data["expires_in"])
            return True
        except Exception as err:
            log.error("authorization_code exchange failed", exc_info=err)
        return False

    async def fetch_username(self):
        log.debug("fetching username")
        try:
            async with await self.get(path="/oauth2/userinfo") as r:
                data = r.json()
            self.set_refresh_token(data["refresh_token"], scopes)
            self.set_access_token(data["access_token"], data["expires_in"])
            return True
        except Exception as err:
            log.error("username fetching failed", exc_info=err)
        return False
