import contextlib

import mysql.connector
import sqlalchemy


@contextlib.contextmanager
def mysql_connector_connection(cfg):
    cnx = mysql.connector.connect(
        database=cfg.get("database"),
        host=cfg.get("host"),
        port=cfg.get("port"),
        user=cfg.get("user"),
        password=cfg.get("password"),
    )

    try:
        yield cnx
    finally:
        cnx.close()


@contextlib.contextmanager
def sqlalchemy_connection(cfg):
    driver = "mysql+pymysql"
    url = sqlalchemy.engine.url.URL(
        driver,
        cfg.get("user"),
        cfg.get("password"),
        cfg.get("host"),
        cfg.get("port"),
        cfg.get("database"),
    )
    engine = sqlalchemy.create_engine(url, echo=False)
    cnx = engine.connect()

    try:
        yield cnx
    finally:
        cnx.close()
        engine.dispose()
