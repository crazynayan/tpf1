from typing import Callable

from munch import Munch

from config import config
from p7_flask_app import tpf1_app
from p7_flask_app.auth import User

CLIENT = tpf1_app.test_client()


def authorized_request(func: Callable, url: str, **kwargs) -> Munch:
    if not config.TEST_TOKEN:
        config.TEST_TOKEN = User.objects.filter_by(email="nayan@crazyideas.co.in").first().token
    kwargs['headers'] = {'Authorization': f"Bearer {config.TEST_TOKEN}"}
    response = func(url, **kwargs)
    if response.status_code == 401:
        config.TEST_TOKEN = str()
    if response.status_code != 200:
        return Munch()
    return Munch.fromDict(response.get_json())


def api_get(url: str, **kwargs):
    return authorized_request(CLIENT.get, url, **kwargs)


def api_post(url: str, **kwargs):
    return authorized_request(CLIENT.post, url, **kwargs)


def api_delete(url: str, **kwargs):
    return authorized_request(CLIENT.delete, url, **kwargs)
