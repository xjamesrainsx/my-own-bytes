from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker


def test_sqla_ext(test_app):
    ext = test_app.extensions['sqla_ext']

    assert isinstance(ext.engine, Engine)
    assert isinstance(ext.session, sessionmaker)