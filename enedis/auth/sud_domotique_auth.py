"""Sud Domotique Enedis Auth."""
from typing import Optional, Union, Callable, Dict

from urllib.parse import urlencode
from requests import Response, Session
from requests_oauthlib import OAuth2Session

from .abstractauth import AbstractAuth, METERING_DATA_BASE_URL_PROD

AUTHORIZE_URL_PROD = "http://www.sud-domotique-expert.fr/enedis/accord_enedis_prod.html"
ENDPOINT_TOKEN_URL_PROD = "http://www.sud-domotique-expert.fr/enedis/enedis_token_prod.php"
# ?refresh_token="+refresh_token
# &box_url="+box_url
# &flow_id="+flow_id


class SudDomotiqueAuth(OAuth2Session):
    """Sud Domotique Enedis Auth."""

    def __init__(
        self,
        redirect_uri: str,
        token: Optional[Dict[str, str]] = None,
        token_updater: Optional[Callable[[Dict[str, str]], None]] = None,
    ):
        self.redirect_uri = redirect_uri
        self.token: Optional[Dict[str, str]] = token or None # Should contain refresh_token + access_token
        self.token_updater = token_updater or self.update_token

        self._session = Session()
        super(SudDomotiqueAuth, self).__init__(
            redirect_uri=redirect_uri,
            token=token,
            token_updater=token_updater
        )

    def authorization_url(self, **kwargs):
        """test state will be appended to state for sandbox testing, it can be 0 to 9"""
        # self._session = Session()
        return AUTHORIZE_URL_PROD + "?"+ urlencode({"redirect_uri": self.redirect_uri, **kwargs})

    def refresh_tokens(self, **kwargs) -> Dict[str, Union[str, int]]:
        """Refresh and return new tokens."""
        url = ENDPOINT_TOKEN_URL_PROD + "?" + urlencode({"refresh_token": self.token["refresh_token"], **kwargs})
        token = self._session.get(url)

        self.token_updater(token)

        return token

    def request(self, path: str, arguments: Dict[str, str]) -> Response:
        """Make a request.
        We don't use the built-in token refresh mechanism of OAuth2 session because
        we want to allow overriding the token refresh logic.
        """
        url = METERING_DATA_BASE_URL_PROD + path
        # This header is required by v3/customers, v4/metering data is ok with the default */*
        headers = {
                'Accept': 'application/json',
                'Content-Type': (
                    'application/x-www-form-urlencoded;charset=UTF-8'
                ),
            }
        response = self._session.get(url, params=arguments, headers=headers)
        if response.status_code == 403:
            self.refresh_tokens()
            return self._session.get(url, params=arguments, headers=headers)
        return response

    def get_usage_point_ids(self):
        """Get the usage point ids."""
        if not self.token or not self.token.get("usage_points_id"):
            return []
        return self.token["usage_points_id"].split(",")

    def close(self):
        if self._session:
            self._session.close()
        self._session = None
