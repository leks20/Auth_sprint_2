import importlib
from urllib import request

from gevent import monkey

monkey.patch_all()

import db
from conf.config import settings
from endpoints.v1.auth import auth
from endpoints.v1.google import google
from endpoints.v1.roles import roles
from flasgger import Swagger
from flask import Flask, request
from flask_jwt_extended import JWTManager
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from tracer import configure_tracer

jwt = JWTManager()
swagger = Swagger()


def register_auth_provider(app, auth_provider):
    blueprint_name = f"{auth_provider}_auth"
    blueprint = importlib.import_module(f"endpoints.v1.{auth_provider}")
    app.register_blueprint(
        getattr(blueprint, blueprint_name), url_prefix=f"/{blueprint_name}"
    )


def create_app():
    if settings.enable_tracer:
        configure_tracer()
    app = Flask(__name__)
    FlaskInstrumentor().instrument_app(app)
    app.debug = True

    if settings.enable_before_request:

        @app.before_request
        def before_request():
            request_id = request.headers.get("X-Request-Id")
            if not request_id:
                raise RuntimeError("Request id is required")

    db.init_db(app)
    jwt.init_app(app)
    swagger.init_app(app)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(roles, url_prefix="/roles")
    register_auth_provider(app, "google")

    app.config["SECRET_KEY"] = settings.secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.access_expires
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.refresh_expires
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
    return app


app = create_app()
