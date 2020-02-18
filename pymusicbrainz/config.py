from .const import (
    MUSICBRAINZ_SERVER_HOST,
    MUSICBRAINZ_SERVER_PORT,
)
from .version import __version__
from collections import UserDict


class Config(UserDict):
    @property
    def refresh_token(self):
        return self.data.get("refresh_token", None)

    @refresh_token.setter
    def refresh_token(self, value):
        self.data["refresh_token"] = value

    @refresh_token.deleter
    def refresh_token(self, value):
        del self.data["refresh_token"]

    @property
    def refresh_token_scopes(self):
        return self.data.get("oauth_refresh_token_scopes", [])

    @refresh_token_scopes.setter
    def refresh_token_scopes(self, value):
        self.data["oauth_refresh_token_scopes"] = value

    @refresh_token_scopes.deleter
    def refresh_token_scopes(self):
        del self.data["oauth_refresh_token_scopes"]

    @property
    def access_token(self):
        return self.data.get("oauth_access_token", None)

    @access_token.setter
    def access_token(self, value):
        self.data["oauth_access_token"] = value

    @access_token.deleter
    def access_token(self):
        del self.data["oauth_access_token"]

    @property
    def access_token_expires(self):
        return self.data.get("oauth_access_token_expires", None)

    @access_token_expires.setter
    def access_token_expires(self, value):
        self.data["oauth_access_token_expires"] = value

    @access_token_expires.deleter
    def access_token_expires(self):
        del self.data["oauth_access_token_expires"]

    @property
    def username(self):
        return self.data["oauth_username"]

    @username.setter
    def username(self, value):
        self.data["oauth_username"] = value

    @property
    def user_agent(self):
        return self.data.get(
            "user_agent",
            f"pymusicbrainz/{__version__} (https://github.com/ibmibmibm/pymusicbrainz)",
        )

    @user_agent.setter
    def user_agent(self, value):
        self.data["user_agent"] = value

    @user_agent.deleter
    def user_agent(self):
        del self.data["user_agent"]

    @property
    def server_host(self):
        return self.data.get("server_host", MUSICBRAINZ_SERVER_HOST)

    @server_host.setter
    def server_host(self, value):
        self.data["server_host"] = value

    @server_host.deleter
    def server_host(self):
        del self.data["server_host"]

    @property
    def server_port(self):
        return self.data.get("server_port", MUSICBRAINZ_SERVER_PORT)

    @server_port.setter
    def server_port(self, value):
        self.data["server_port"] = value

    @server_port.deleter
    def server_port(self):
        del self.data["server_port"]

    @property
    def rate_limit_interval(self):
        return self.data.get("rate_limit_interval", 1)

    @rate_limit_interval.setter
    def rate_limit_interval(self, value):
        self.data["rate_limit_interval"] = value

    @rate_limit_interval.deleter
    def rate_limit_interval(self):
        del self.data["rate_limit_interval"]
