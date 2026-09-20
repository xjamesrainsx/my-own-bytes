import waitress
from dotenv import load_dotenv
from flask import Flask


def reg_blueprints(app: Flask):
    """Registers blueprints to application when create_app is called"""

    from myownbytes.webhook_server.webhooks_bp import webhooks_bp

    bps = (
        webhooks_bp,
    )

    for bp in bps:
        app.register_blueprint(bp)

def reg_extensions(app: Flask):
    """Registers extensions to application when create_app is called"""
    from myownbytes.extensions.plaid_ext import plaid_ext
    from myownbytes.extensions.sqla_ext import sqla_ext

    exts = (
        sqla_ext,
        plaid_ext
    )

    for ext in exts:
        app.extensions[ext._name] = ext
        ext.init_app_(app)

def reg_config(app: Flask):
    """
    Loads a configuration from .env file
    based on app.config['CONF'] assignment. 
    app.config['CONF'] is assigned the string 
    passed to the application factory, if any.
    """
    if app.testing:
        app.config.from_prefixed_env("TEST")
    else:
        app.config.from_prefixed_env()

def app_init(config: str | None = None)-> Flask:
    """
    Initializes a Flask application based on the
    configuration string passed to the app factory.

    :param: config: str -- "test" | "dev" | None

    :returns: app: Flask
    """
    
    app = Flask('webhook-server')
    if config == "test":
        app.testing = True

    load_dotenv()
    reg_config(app)
    reg_extensions(app)
    reg_blueprints(app)
    
    return app

def serve():
    """Run webhook listener"""
    app = app_init()
    waitress.serve(app, host="0.0.0.0",port=5000)

def test():
    app = app_init("test")
    app.run()

def dev():
    app = app_init("test")
    app.testing = False
    app.run(debug=True)