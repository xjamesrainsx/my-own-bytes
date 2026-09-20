from sqlalchemy import create_engine, select
from sqlalchemy.orm import session, sessionmaker

from myownbytes.models.model import (
    Auth,
    Base,
    Item,
    ItemCursor,
    Transaction,
    Webhook,
)


class SQLAlchemy:
    def __init__(self):
        self._name: str = "sqla_ext"
        self.engine = None
        self.session = None

    def init_app_(self, app):
        self.engine = create_engine(app.config['DB_URI'])
        self.session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

        @app.teardown_appcontext
        def shutdown_session(e=None):
            app.logger.debug("Tearing down sessions")
            session.close_all_sessions()
        return self

    def add_webhook(self, webhook):
        assert self.session is not None
        with self.session.begin() as sesh:
            sesh.add(Webhook.from_json(webhook))

    def add_liabilities(self, liabilities):
        assert self.session is not None
        with self.session.begin() as sesh:
            sesh.add_all(liabilities)

    def add_accounts(self, accounts):
        assert self.session is not None
        with self.session.begin() as sesh:
            sesh.add_all(accounts)

    def add_item(self, item_data):
        assert self.session is not None
        with self.session.begin() as sesh:
            sesh.add_all(item_data)

    def add_balances(self, balances):
        assert self.session is not None
        with self.session.begin() as sesh:
            sesh.add_all(balances)

    def update_item_cursor(self, item_id, next_cursor):
        assert self.session is not None
        with self.session.begin() as sesh:
            cursor = sesh.get(
                ItemCursor, item_id)
            if cursor:
                cursor.next_cursor = next_cursor
            else:
                cursor = ItemCursor(
                    item_id=item_id, 
                    next_cursor=next_cursor)
            sesh.add(cursor)
        
    def get_item_cursor(self, item_id):
        assert self.session is not None
        with self.session.begin() as sesh:
            cursor = sesh.get(
                ItemCursor, item_id)
            if cursor:
                return cursor.next_cursor

    def reverse_item_lookup(self, access_token):
        assert self.session is not None
        stmt = select(Auth).where(
            Auth.access_token == access_token)
        with self.session.begin() as sesh:
            auth = sesh.scalars(stmt).one()
            return auth.item_id
            
    def get_item_auth(self, item_id):
        assert self.session is not None
        with self.session.begin() as sesh:
            auth = sesh.get_one(Auth, item_id)
            return auth.access_token

    def add_transactions_to_db(self, txn_data: dict[str,list]):
        assert self.session is not None
        for txntype,txns in txn_data.items():
            if len(txns) > 0:
                for txn in txns:
                    with self.session.begin() as sesh:
                        stored_txn = sesh.get(
                            Transaction,
                            txn['transaction_id']
                            )
                    
                    match txntype:
                        case "remove":
                            with self.session.begin() as sesh:
                                sesh.delete(stored_txn)
                        case "modified":
                            if stored_txn:
                                stored_txn = txn
                            with self.session.begin() as sesh:
                                sesh.add(stored_txn)
                        case "added":
                            with self.session.begin() as sesh:
                                sesh.add(Transaction.from_json(txn))

    def update_item_webhook(self, item_id, webhook):      
        assert self.session is not None
        with self.session.begin() as sesh:
            item = sesh.get_one(
                Item, item_id)
            item.webhook = webhook
            sesh.add(item)
        
sqla_ext = SQLAlchemy()