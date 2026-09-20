import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


def CST_NOW():
    cst = timezone(offset=timedelta(hours=-5))
    dt = datetime.now(tz=cst)
    return dt.isoformat(timespec="milliseconds")

class Base(DeclarativeBase,MappedAsDataclass):
    @classmethod
    def from_json(cls, response, **kwargs):
        """
        Parse JSON to model instance.
        This class method takes a dictionary and
        any kw argument, compares the keys to a 
        list of target keys that is generated from
        the dataclass fields of the the calling
        class.
        """

        target_keys = [
            field_name for field_name, field 
            in cls.__dataclass_fields__.items()
            ]
 
        extractor = cls._Extractor(target_keys)
        if response:
            json.loads(
                json.dumps(response),
                object_hook=extractor.hook)

        if kwargs:
            for k,v in kwargs.items():
                if k in target_keys:
                    extractor.found[k] = v
 
        return cls(**extractor.found)
    
    class _Extractor:
        def __init__(self, target_keys):
            self.target_keys = set(target_keys)  
            self.found = {}
        
        def hook(self, dct):
            for k, v in dct.items():
                if k in self.target_keys:
                    if isinstance(v, list):
                        self.found[k] = ', '.join(v)
                    else:
                        self.found[k] = v
            return dct

class Webhook(Base):
    """
    Model to store received webhooks 
    """
    __tablename__ = "webhook"

    id: Mapped[int] = mapped_column(primary_key=True, init=False, autoincrement=True)
    environment: Mapped[str]
    item_id: Mapped[str] 
    webhook_code: Mapped[str]
    webhook_type: Mapped[str] 
    timestamp: Mapped[int] = mapped_column(default=CST_NOW())
    
class Auth(Base):
    """
    Model to store encrypted item accesstoken pairs
    """
    __tablename__ = "auth"

    item_id: Mapped[str] = mapped_column(primary_key=True)
    access_token: Mapped[str]

class ItemCursor(Base):
    """
    Model to store plaid item cursors
    """
    __tablename__= "cursor"

    item_id: Mapped[str] = mapped_column(primary_key=True)
    next_cursor: Mapped[str]
    timestamp: Mapped[str] = mapped_column(init=False, default=None, insert_default=CST_NOW())

class ItemProductStatus(Base):
    """
    Model to store plaid item product information
    """
    __tablename__ = "itemproductstatus"
    
    item_id: Mapped[str] = mapped_column(primary_key=True)
    products: Mapped[str | None] = mapped_column(default=None)
    available_products: Mapped[str | None] = mapped_column(default=None)
    billed_products: Mapped[str | None] = mapped_column(default=None)
    consented_products: Mapped[str | None] = mapped_column(default=None)
    consent_expiration_time: Mapped[str | None] = mapped_column(default=None)

class Item(Base):
    """
    Model to store plaid items 
    """
    __tablename__ = "item"

    item_id: Mapped[str] = mapped_column(primary_key=True)
    webhook: Mapped[str | None]
    institution_id: Mapped[str] 
    institution_name: Mapped[str] 
    
class Account(Base):
    """
    Model to store plaid accounts 
    """
    __tablename__ = "account"

    account_id: Mapped[str] = mapped_column(primary_key=True)
    item_id: Mapped[str | None]
    name: Mapped[str | None]
    official_name: Mapped[str | None]
    mask: Mapped[str | None] 
    type: Mapped[str | None] 
    subtype: Mapped[str | None]


class Balance(Base):
    """
    Model to store plaid balances 
    """
    __tablename__ = "balance"

    id: Mapped[int] = mapped_column(primary_key=True, init=False, autoincrement=True)
    account_id: Mapped[str]
    available: Mapped[float | None]
    current: Mapped[float | None]
    limit: Mapped[float | None] 
    timestamp: Mapped[int] = mapped_column(default=CST_NOW())

class Transaction(Base):
    """
    Model to store plaid transactions 
    """
    __tablename__ = "transaction"

    transaction_id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str]
    amount: Mapped[float]
    date: Mapped[str]
    merchant_name: Mapped[str | None]
    pending: Mapped[bool]
    pending_transaction_id: Mapped[str | None]
    primary: Mapped[str]
    detailed: Mapped[str]


class Liability(Base):
    """
    Model to store plaid liabilities 
    """
    __tablename__ = "liability"

    id: Mapped[int] = mapped_column(primary_key=True, init=False, autoincrement=True)
    account_id: Mapped[str]
    is_overdue: Mapped[bool | None] = mapped_column(default=None)
    last_payment_amount: Mapped[float | None] = mapped_column(default=None)
    last_payment_date: Mapped[str | None] = mapped_column(default=None)
    last_statement_balance: Mapped[float | None]  = mapped_column(default=None)
    last_statement_issue_date: Mapped[str | None] = mapped_column(default=None)
    minimum_payment_amount: Mapped[float | None] = mapped_column(default=None)
    next_payment_due_date: Mapped[str | None] =  mapped_column(default=None)
    timestamp: Mapped[str] = mapped_column(default=None,insert_default=CST_NOW())