"""Basic Enedis Auth."""
from typing import Optional, Union, Callable, Dict

from urllib.parse import urlencode
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError


AUTHORIZE_URL_SANDBOX = "https://gw.hml.api.enedis.fr/dataconnect/v1/oauth2/authorize"
ENDPOINT_TOKEN_URL_SANDBOX = "https://gw.hml.api.enedis.fr/v1/oauth2/token"
METERING_DATA_BASE_URL_SANDBOX = "https://gw.hml.api.enedis.fr"

AUTHORIZE_URL_PROD = "https://gw.prd.api.enedis.fr/dataconnect/v1/oauth2/authorize"
ENDPOINT_TOKEN_URL_PROD = "https://gw.prd.api.enedis.fr/v1/oauth2/token"
METERING_DATA_BASE_URL_PROD = "https://gw.prd.api.enedis.fr"


class AbstractAuth(OAuth2Session):
    """Basic Enedis Auth."""

    def __init__(
        self,
        token: Optional[Dict[str, str]] = None,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        token_updater: Optional[Callable[[str], None]] = None,
        sandbox: bool = False,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater
        self.sandbox = sandbox

        extra = {"client_id": self.client_id, "client_secret": self.client_secret}

        super(AbstractAuth, self).__init__(
            client_id=client_id,
            auto_refresh_kwargs=extra,
            redirect_uri=redirect_uri,
            token=token,
            token_updater=token_updater
        )

    def authorization_url(self, duration: str = "", test_customer: str = ""):
        """test state will be appended to state for sandbox testing, it can be 0 to 9"""
        url = AUTHORIZE_URL_PROD
        if self.sandbox:
            url = AUTHORIZE_URL_SANDBOX
        state = self.new_state()
        if test_customer:
            state = state + test_customer
        return super(AbstractAuth, self).authorization_url(url, duration=duration, state=state)

    def refresh_tokens(self) -> Dict[str, Union[str, int]]:
        """Refresh and return new tokens."""
        url = ENDPOINT_TOKEN_URL_PROD
        if self.sandbox:
            url = ENDPOINT_TOKEN_URL_SANDBOX
        if self.redirect_uri is not None:
            url = url + "?" + urlencode({"redirect_uri": self.redirect_uri})
        token = super(AbstractAuth, self).refresh_token(
            url,
            include_client_id=True,
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.token["refresh_token"],
        )

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def request_tokens(self, code) -> Dict[str, Union[str, int]]:
        """return new tokens."""
        url = ENDPOINT_TOKEN_URL_PROD
        if self.sandbox:
            url = ENDPOINT_TOKEN_URL_SANDBOX
        if self.redirect_uri is not None:
            url = url + "?" + urlencode({"redirect_uri": self.redirect_uri})
        token = super(AbstractAuth, self).fetch_token(
            url,
            include_client_id=True,
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code,
        )

        if self.token_updater is not None:
            self.token_updater(token)
        return token

    def request(self, path: str, arguments: Dict[str, str]) -> Response:
        """Make a request.
        We don't use the built-in token refresh mechanism of OAuth2 session because
        we want to allow overriding the token refresh logic.
        """
        url = METERING_DATA_BASE_URL_PROD
        if self.sandbox:
            url = METERING_DATA_BASE_URL_SANDBOX
        url = url + path
        # This header is required by v3/customers, v4/metering data is ok with the default */*
        headers = {"Accept": "application/json"}
        try:
            response = super(AbstractAuth, self).request(
                "GET", url, params=arguments, headers=headers
            )
            if response.status_code == 403:
                self.token = self.refresh_tokens()
            else:
                return response
        except TokenExpiredError:
            self.token = self.refresh_tokens()

        return super(AbstractAuth, self).request("GET", url, params=arguments, headers=headers)

    def get_usage_point_ids(self):
        """Get the usage point ids."""
        if not self.token or not self.token.get("usage_points_id"):
            return []
        return self.token["usage_points_id"].split(",")

