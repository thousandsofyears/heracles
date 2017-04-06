# -*- coding: utf-8 -*-
from flask import Flask

from database import db
from flask_migrate import Migrate
from heracles_v1 import bp
from config import Config


def create_app(config=None):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    db.init_app(app)
    Migrate().init_app(app, db)

    app.register_blueprint(
        bp,
        url_prefix='/heracles_v1')
    return app
