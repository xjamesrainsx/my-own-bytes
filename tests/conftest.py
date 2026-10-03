import flask
import pytest
from dotenv import dotenv_values

from myownbytes.plaidrunner import make_app
from myownbytes.webhook_server import app_init


@pytest.fixture
def server_app():
    app = app_init("test")
    assert app.debug == False
    assert app.testing == True
    yield app

@pytest.fixture
def plaidrunner_app():
    app = make_app("test")
    assert app.debug == False
    assert app.testing == True
    yield app

@pytest.fixture
def access_token():
    return dotenv_values()['TEST_ACCESS_TOKEN']

@pytest.fixture
def client(server_app):
    return flask.Flask.test_client(server_app)

@pytest.fixture
def cli_runner(plaidrunner_app):
    return flask.Flask.test_cli_runner(plaidrunner_app)
 
