import json

import click
from flask import Blueprint

from myownbytes.extensions.plaid_ext import plaid_ext as pr
from myownbytes.extensions.sqla_ext import sqla_ext as sq
from myownbytes.models.model import (
    Account,
    Auth,
    Balance,
    Item,
    ItemProductStatus,
    Liability,
)

plaidrunner_bp = Blueprint('runner', __name__)

@plaidrunner_bp.cli.command("fire-wh")
@click.argument("access_token")
@click.argument("wh_type")
@click.argument("wh_code")
def fire_sandbox_webhook(access_token, wh_type, wh_code):
    """
    Fire a sandbox plaid webhook 
    at dev or testing server.

    :param str access_token: A valid plaid access_token.

    :param str wh_type: A valid webhook type.

    :param str wh_code: A valid webhook code. 
    """ 
    try:
        res = pr.sandbox_fire_webhook(
            access_token=access_token,
            webhook_type = wh_type,
            webhook_code = wh_code
        )

        click.echo(json.dumps(res.json(), indent=4))
    
    except Exception as e:  # noqa: BLE001
        click.echo(e)
    
@plaidrunner_bp.cli.command("update-wh") 
@click.argument("access_token")
@click.argument("webhook")
def update_webhook(access_token, webhook): 
    """
    Add or update an item's webhook.
    
    :param str access_token: A valid plaid access_token.

    :param str webhook: Must include https://
    """
    try:
        res = pr.update_webhook(
            access_token=access_token,
            webhook = webhook
        )
        assert res.json().get('error') == None
        item_id = sq.reverse_item_lookup(
            access_token=access_token,
        )
        sq.update_item_webhook(item_id, webhook)
    except Exception as e:  # noqa: BLE001
        click.echo(e)

@plaidrunner_bp.cli.command("get-item")
@click.argument("access_token")
@click.option('-a', is_flag=True)
def add_item(access_token, a=None): 
    """
    Retrieve an item using an existing 
    access_token. Commit to database 
    if flagged. 

    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    try:
        # Calling plaid item endpoint.
        res = pr.item_get(
            access_token= access_token
            )
        item = Item.from_json(res.json())
        prod = ItemProductStatus.from_json(res.json())
        auth = Auth(item.item_id,access_token)
        item_data = (item, prod, auth)

        click.echo("get item")

        if a:
            sq.add_item(item_data)

    except Exception as e:  # noqa: BLE001
        click.echo(e)

@plaidrunner_bp.cli.command("get-accounts")
@click.argument("access_token")
@click.option('-a', is_flag=True)
def add_accounts(access_token, a=None):
    """
    Retrieve an item's accounts 
    using an existing access_token.
    Commit to database if flagged. 

    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    # Calling plaid accounts endpoint.
    try:
        res = pr.accounts_get(access_token = access_token)
        item_id = res.json()['item']['item_id']
        accounts = [
            Account.from_json(account, item_id=item_id) 
            for account in res.json()['accounts']]
        
        click.echo("get accounts")

        if a:
            sq.add_accounts(accounts)

    except Exception as e:  # noqa: BLE001
        click.echo(e)

@plaidrunner_bp.cli.command("get-liabilities")
@click.argument("access_token")
@click.option('-a', is_flag=True)
def add_liabilities(access_token, a= None):
    """
    Retrieve an item's liabilities 
    using an existing access_token
    and commit to database. 
    
    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    try:
        # Calling plaid liabilities endpoint.
        res = pr.liability_get(access_token = access_token)
        liabilities = [
            Liability.from_json(liability) for liab in 
            res.json()['liabilities'].values() 
            for liability in liab
            ]
        
        click.echo("get liabilities")

        if a:
            sq.add_liabilities(liabilities)

    except Exception as e:  # noqa: BLE001
        click.echo(e)


@plaidrunner_bp.cli.command("get-balances")
@click.argument("access_token")
@click.option('-a', is_flag=True)
def add_balances(access_token, a= None):
    """
    Retrieve an item's balances 
    using an existing access_token
    and commit to database. 
    
    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    try:
        res = pr.balance_get(access_token = access_token)
        balances = [
            Balance.from_json(balance) for balance 
            in res.json()['accounts']
            ]

        click.echo("get balances")

        if a:
            sq.add_balances(balances)

    except Exception as e:  # noqa: BLE001
        click.echo(e)

@plaidrunner_bp.cli.command("sync-txns")
@click.argument("access_token")
@click.option('-a', is_flag=True)
def sync_transactions(access_token, a= None):
    """
    Retrieve an item's transactions 
    using an existing access_token and
    cursor. Commit to database if selected.

    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    try:
        has_more = True
        item_id = sq.reverse_item_lookup(access_token)
        cursor = sq.get_item_cursor(item_id)
        txn_data = {"added":[],"modified":[],"removed":[]}
        while has_more:    
            res = pr.transaction_sync(
                access_token = access_token,
                cursor = cursor
                )
            txn_data['added'] += res.json()['added']
            txn_data['modified'] += res.json()['modified']
            txn_data['removed'] += res.json()['removed']
            next_cursor = res.json()['next_cursor']
            has_more = res.json()['has_more']
        if a:
            sq.update_item_cursor(item_id, next_cursor)
            sq.add_transactions_to_db(txn_data)

    except Exception as e:  # noqa: BLE001
       click.echo(e)

