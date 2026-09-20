import hashlib
import hmac
import time

import jwt
from flask import Blueprint, current_app, jsonify
from flask import request as req
from sqlalchemy.exc import SQLAlchemyError

from myownbytes.extensions.plaid_ext import plaid_ext as pr
from myownbytes.extensions.sqla_ext import sqla_ext as sq

webhooks_bp = Blueprint('webhooks',__name__)

def verify_wh(data, headers):
    plaid_jwt = headers.get('Plaid-Verification', None)

    if plaid_jwt is None:
        current_app.logger.debug(
            f"Bad jwt. {plaid_jwt}"
            )
        return False

    jwt_headers = jwt.get_unverified_header(
        plaid_jwt
        )

    plaid_jwk = pr.webhook_key_get(
        key_id = jwt_headers['kid']
        )

    if not plaid_jwk.ok:
        current_app.logger.debug(
            f"Bad key request. {plaid_jwk}"
            )
        return False
    
    jwk = jwt.PyJWK(plaid_jwk.json()['key'])

    # Validate the signature and extract the claims.
    try:
        claims = jwt.decode(plaid_jwt, jwk)
    except jwt.PyJWTError as e:
        current_app.logger.debug(f"PyJWTError {e}")
        return False

    # Ensure that the token is not expired.
    if claims["iat"] < time.time() - 5 * 60:
        current_app.logger.debug(
            """
            Claims are stale.
            Not trusting it.
            """
        )
        return False
    
    # Compute the hash of the body.
    m = hashlib.sha256(data)
    body_hash = m.hexdigest()

    # Ensure that the hash of the body matches the claim.
    return hmac.compare_digest(
        body_hash, 
        claims['request_body_sha256']
        )

def process_sync_updates_available(item_id):
    """
    Retrieve an item's transactions 
    using an existing access_token and
    cursor. Commit to database if selected.

    :param str access_token: A valid plaid access_token

    :param bool a: Add response to database.
    """
    try:
        has_more = True
        access_token = sq.get_item_auth(item_id)
        cursor = sq.get_item_cursor(item_id)
        txn_data = {"added":[],"modified":[],"removed":[]}
        while has_more:    
            res = pr.transaction_sync(
                access_token = access_token,
                cursor = cursor 
                if cursor else ""
                )
            txn_data['added'] += res.json()['added']
            txn_data['modified'] += res.json()['modified']
            txn_data['removed'] += res.json()['removed']
            next_cursor = res.json()['next_cursor']
            has_more = res.json()['has_more']
    
        sq.update_item_cursor(item_id, next_cursor)
        sq.add_transactions_to_db(txn_data)

    except Exception as e:  # noqa: BLE001
        current_app.logger.debug(e)

def process_webhook(web_hook):
    try:
        sq.add_webhook(web_hook)

        match web_hook['webhook_type']:
            case "TRANSACTIONS":
                if web_hook['webhook_code'] == ("SYNC_UPDATES_AVAILABLE"):
                        process_sync_updates_available(web_hook['item_id'])

            case "LIABILITIES":
                pass
            
            case _:
                current_app.logger.info(
                    """
                    No Matching Commands Found. 
                    Awaiting another hook.
                    """
                )
                current_app.logger.info(web_hook)

    except SQLAlchemyError as e:
        current_app.logger.debug(e)

@webhooks_bp.post('/webhooks')
def webhooks():
    try:
        # Pre-verification request checks
        if not req.is_json:
            raise RuntimeError("The webhook content type is wrong")
        
        elif not req.json.get('environment', None) :
            raise RuntimeError("The webhook env is None")
        
        elif (req.json.get('environment', None) 
              != current_app.config['PLAID_ENV']):
            current_app.logger.info("The webhook env is wrong")
            return jsonify({"status": "success"}), 200

        elif not verify_wh(req.data,req.headers):
                raise RuntimeError("The webhook could not be verified")
        
        else:
            process_webhook(req.json)
            return jsonify({"status": "success"}), 200
        
    except RuntimeError as e:
        current_app.logger.debug(e)
        return jsonify({"status": "bad_request"}), 400
