import requests
from requests.auth import AuthBase


def checked(resp: requests.Response) -> requests.Response:
    resp.raise_for_status()
    return resp


AUTHORIZATION_HEADER = "Authorization"


class BearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, request: requests.Request) -> requests.Request:
        request.headers[AUTHORIZATION_HEADER] = f"Bearer {self.token}"
        return request