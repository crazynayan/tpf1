from typing import Callable

from munch import Munch

from p7_flask_app import tpf1_app
from p7_flask_app.auth import User

CLIENT = tpf1_app.test_client()

TOKEN_CACHE: Munch = Munch()
def authorized_request(func: Callable, url: str, email: str, **kwargs) -> Munch:
    if "api_other_auth" in kwargs:
        token = User.objects.filter_by(email="john.stack@smltd.com").first().token
        del kwargs["api_other_auth"]
    else:
        if email not in TOKEN_CACHE:
            TOKEN_CACHE[email] = User.objects.filter_by(email=email).first().token
        token = TOKEN_CACHE[email]
    kwargs['headers'] = {'Authorization': f"Bearer {token}"}
    response = func(url, **kwargs)
    if response.status_code == 401 and email in TOKEN_CACHE:
        del TOKEN_CACHE[email]
    if response.status_code != 200:
        return Munch()
    return Munch.fromDict(response.get_json())


def api_get(url: str, **kwargs):
    return authorized_request(CLIENT.get, url, email="nayan@crazyideas.co.in", **kwargs)


def api_post(url: str, **kwargs):
    return authorized_request(CLIENT.post, url, email="nayan@crazyideas.co.in", **kwargs)


def api_post_using_general_domain_auth(url: str, **kwargs):
    return authorized_request(CLIENT.post, url, email="info@crazyideas.co.in", **kwargs)


def api_delete(url: str, **kwargs):
    return authorized_request(CLIENT.delete, url, email="nayan@crazyideas.co.in", **kwargs)
