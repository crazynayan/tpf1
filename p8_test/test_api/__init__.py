from functools import wraps
from random import choice
from unittest import TestCase

from config import config
from p7_flask_app import tpf1_app
from p7_flask_app.api.api0_constants import NAME
from p7_flask_app.auth import User


def authenticated_request(func):
    @wraps(func)
    def request_wrapper(self, url: str, **kwargs):
        if not config.TEST_TOKEN:
            config.TEST_TOKEN = User.objects.filter_by(email="nayan@crazyideas.co.in").first().token
        kwargs['headers'] = {'Authorization': f"Bearer {config.TEST_TOKEN}"}
        response = func(self, url, **kwargs)
        if response.status_code == 401:
            config.TEST_TOKEN = str()
        return response

    return request_wrapper


class TestAPI(TestCase):
    NAME = "NZ99 - ETA5 - Testing 123"
    SEG_NAME = "ETA5"
    NAME_100 = "NZ99 - a valid name with 100 characters - "
    NAME_100 = f"{NAME_100}{''.join([str(choice(range(10))) for _ in range(100 - len(NAME_100))])}"
    NAME_101 = "NZ99 - an invalid name with 101 characters - "
    NAME_101 = f"{NAME_101}{''.join([str(choice(range(10))) for _ in range(101 - len(NAME_101))])}"

    def setUp(self):
        self.client = tpf1_app.test_client()
        self.cleanup = list()

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", query_string={NAME: name})

    @authenticated_request
    def get(self, url: str, **kwargs):
        return self.client.get(url, **kwargs)

    @authenticated_request
    def post(self, url: str, **kwargs):
        return self.client.post(url, **kwargs)

    @authenticated_request
    def delete(self, url: str, **kwargs):
        return self.client.delete(url, **kwargs)
