import logging
import aiohttp_cors

from aiohttp import web
from aiohttp_basicauth_middleware import basic_auth_middleware
from bert_serving.client import BertClient
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY
from .api import routes


logger = logging.getLogger(__name__)


def setup_cors(app):
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_methods="*",
                allow_headers="*",
            )
        },
    )
    for route in app.router.routes():
        cors.add(route)


def bert_session(config):
    """Create bert connection

    Args:
        config (object): API configuration object

    Returns:
        bert_serving.client.BertClient: BertClient
    """
    return BertClient(ip=config.BERT_HOST)


def db_session(config):
    """Create database connection

    Args:
        config (object): API configuration object

    Returns:
        Engine
    """
    return create_engine(f"sqlite:///{config.DB_PATH}", strategy=ASYNCIO_STRATEGY)


def create_app(config):
    """Create aiohttp application instance

    Args:
        config (object): API configuration object

    Returns:
        aiohttp.web.Application: API
    """
    app = web.Application()

    app["bert"] = bert_session(config)
    app["db"] = db_session(config)
    app["config"] = config

    # Routes
    app.add_routes(routes)
    # Middlewares
    # app.middlewares.append(basic_auth_middleware(("/"), {"bot": "bottrick"}))
    setup_cors(app)
    return app
