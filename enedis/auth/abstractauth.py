"""Basic Enedis Auth."""
from typing import Optional, Union, Callable, Dict

from urllib.parse import urlencode
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError

import logging
_LOGGER = logging.getLogger(__name__)


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
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        token: Optional[Dict[str, str]] = None,
        token_updater: Optional[Callable[[str], None]] = None,
        sandbox: bool = False,
        authorize_url: str = None,
        token_url: str = None,
        extra_params: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater or self.update_token

        # Custom Linky
        self.sandbox = sandbox
        self.authorize_url = authorize_url or AUTHORIZE_URL_PROD if not sandbox else AUTHORIZE_URL_SANDBOX
        self.token_url = token_url or ENDPOINT_TOKEN_URL_PROD if not sandbox else ENDPOINT_TOKEN_URL_SANDBOX
        self.extra_params = extra_params or {}

        extra = {"client_id": self.client_id, "client_secret": self.client_secret}

        _LOGGER.warning("AbstractAuth.init")
        _LOGGER.warning(redirect_uri)
        _LOGGER.warning(self.authorize_url)
        _LOGGER.warning(self.token_url)

        super(AbstractAuth, self).__init__(
            client_id=client_id,
            auto_refresh_kwargs=extra,
            redirect_uri=redirect_uri,
            token=token,
            token_updater=token_updater
        )
    
    def update_token(self, token: Dict[str, str]):
        """Update tokens."""
        self.token = token

    def authorization_url(self, duration: str = None, test_customer: str = None, params: Dict[str, str] = None):
        """test state will be appended to state for sandbox testing, it can be 0 to 9"""
        state = self.new_state()
        if test_customer:
            state = state + test_customer
        
        params = params or {}
        params.update({"redirect_uri": self.redirect_uri})
        params.update(self.extra_params)
        url = self.authorize_url + "?" + urlencode(params)

        return super(AbstractAuth, self).authorization_url(
            url,
            redirect_uri=self.redirect_uri,
            state=state,
            duration=duration,
        )

    def refresh_tokens(self, params: Dict[str, str] = None) -> Dict[str, Union[str, int]]:
        """Refresh and return new tokens."""
        params = params or {}
        params.update({"redirect_uri": self.redirect_uri})
        params.update(self.extra_params)
        url = self.token_url + "?" + urlencode(params)

        token = super(AbstractAuth, self).refresh_token(
            url,
            include_client_id=True,
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.token["refresh_token"],
        )

        if self.token_updater:
            self.token_updater(token)

        return token

    def request_tokens(self, code, params: Dict[str, str] = None) -> Dict[str, Union[str, int]]:
        """Return new tokens."""
        params = params or {}
        params.update({"redirect_uri": self.redirect_uri})
        params.update(self.extra_params)
        url = self.token_url + "?" + urlencode(params)

        token = super(AbstractAuth, self).fetch_token(
            url,
            include_client_id=bool(self.client_id),
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code,
        )

        if self.token_updater:
            self.token_updater(token)

        return token

    def request(self, path: str, params: Dict[str, str]) -> Response:
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
                "GET",
                url,
                params=params,
                headers=headers
            )
            if response.status_code == 403:
                self.token = self.refresh_tokens()
            else:
                return response
        except TokenExpiredError:
            self.token = self.refresh_tokens()

        return super(AbstractAuth, self).request(
            "GET",
            url,
            params=params,
            headers=headers
        )

    def get_usage_point_ids(self):
        """Get the usage point ids."""
        if not self.token or not self.token.get("usage_points_id"):
            return []
        return self.token["usage_points_id"].split(",")

