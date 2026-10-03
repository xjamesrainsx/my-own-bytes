import pytest
from dotenv import dotenv_values

from myownbytes.extensions.plaid_ext import plaid_ext as pe


@pytest.fixture
def plaid_ext():
    pe.host = dotenv_values()['TEST_PLAID_HOST']
    pe.client_id = dotenv_values()['TEST_PLAID_CLIENT']
    pe.secret = dotenv_values()['TEST_PLAID_SECRET']
    return pe

def test_plaid_ext_update_webhook_endpoint(plaid_ext, access_token):
    webhook = "https://sandbox.myownbytes.work/webhooks"
    res = plaid_ext.update_webhook(
        access_token=access_token, webhook=webhook)
    assert res.json()['item']['webhook'] == webhook
    
def test_plaid_ext_item_endpoint(plaid_ext, access_token):

    res = plaid_ext.item_get(access_token=access_token)
    assert len(res.json()) == 3
    assert res.json().get("item") != None
    assert res.json().get("error_type", None) == None

def test_plaid_ext_accounts_endpoint(plaid_ext, access_token):

    res = plaid_ext.accounts_get(access_token=access_token)
    assert len(res.json()) == 3
    assert res.json().get("accounts") != None
    assert res.json().get("item") != None
    assert res.json().get("error_type", None) == None

def test_plaid_ext_balances_endpoint(plaid_ext, access_token):

    res = plaid_ext.balance_get(access_token=access_token)
    assert res.json()["accounts"]
    assert res.json()['item']
    assert res.json()['request_id']
    assert res.json().get("error_type", None) == None

def test_plaid_ext_transactions_endpoint(plaid_ext, access_token):

    res = plaid_ext.transaction_sync(access_token=access_token)
    assert len(res.json()) == 8
    assert res.json().get("accounts") 
    assert res.json().get("has_more") != None
    assert res.json().get("error_type", None) == None
