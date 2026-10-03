from requests import request


class PlaidPython:
    def __init__(self):
        self._name = "plaid_ext"
        self._client_id = None
        self._secret = None
        self._host = None

    def init_app_(self, app):
        self.client_id = app.config['PLAID_CLIENT']
        self.secret = app.config['PLAID_SECRET']
        self.host = app.config['PLAID_HOST']
        return self
    
    def _request(self, path, **kwargs):
        return request(
            method='POST',
            url=f'{self.host}{path}',
            headers={'Content-Type': 'application/json'},
            json={
                'client_id': self.client_id,
                'secret': self.secret,
                **kwargs,
            },
        )

    def webhook_key_get(self, **kwargs):
        """
        Send an http request to webhook_verification_key/get
        endpoint on plaid server.

        :param str key_id: Plaid key id from header
        """
        return self._request(
            'webhook_verification_key/get',
            **kwargs,
        )
    
    def update_webhook(self, **kwargs):
        """
        Update a webhook associated with an item
        
        :param str access_token: A valid plaid access_token.

        :param str webhook: A fully formed https url.
        """
        return self._request(
            'item/webhook/update',
            **kwargs,
        )

    def sandbox_fire_webhook(self, **kwargs):
        """
        Send an http request to sandbox/item/fire_webhook
        endpoint on plaid server.

        :param str access_token:

        :param str webhook_type:

        :param str webhook_code:
        """
        return self._request(
            'sandbox/item/fire_webhook',
            **kwargs,
        )

    def item_get(self, **kwargs):
        """
        Send an http request to item/get
        endpoint on plaid server.

        :param str access_token:

        """
        return self._request(
            'item/get',
            **kwargs,
        )

    def accounts_get(self, **kwargs):
        """
        Send an http request to accounts/get
        endpoint on plaid server.
        
        :param str access_token:
        """
        return self._request(
            'accounts/get',
            **kwargs,
        )

    def balance_get(self, **kwargs):
        """
        Send an http request to accounts/balance/get
        endpoint on plaid server.

        :param str access_token:
        """
        return self._request(
            'accounts/balance/get',
            **kwargs,
        )

    def liability_get(self, **kwargs):
        """
        Send an http request to liabilities/get
        endpoint on plaid server.

        :param str access_token:
        """
        return self._request(
            'liabilities/get',
            **kwargs,
        )

    def transaction_sync(self, **kwargs):
        """
        Send an http request to transactions/sync
        endpoint on plaid server.

        :param str access_token:
        """
        return self._request(
            'transactions/sync',
            **kwargs,
        )

plaid_ext = PlaidPython()
