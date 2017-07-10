# -*- coding: utf-8 -*-
from flask import Flask
from flask_migrate import Migrate
from config import Config
from heracles.core.database import db


def create_app(config=None):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    db.init_app(app)
    Migrate().init_app(app, db)

    import v1
    app.register_blueprint(
        v1.bp,
        url_prefix='/v1')
    return app


if __name__ == '__main__':
    create_app().run(debug=True)
