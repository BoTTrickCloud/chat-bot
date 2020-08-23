"""Main module for starting the API service as Python module.

.. code:: bash

    python -m api

"""
import asyncio
import logging
import os
from aiohttp import web

from . import config_default
from .logger import setup_logging
from .app import create_app
from .utils import faiss_init


logger = logging.getLogger(__name__)


def load_config(config):
    """Load API configuration settings

    VStream default configuration settings is defined by `config_default.py` configuration file.
    The default configuration values can be overwritten by values loaded from
    environment variables.

    Args:
        config (object):  API default configuration object

    Returns:
        object: API configuration

    """
    for key in dir(config):
        if key.isupper():
            try:
                value = os.environ[key]
            except KeyError:
                continue

            setattr(config, key, value)

    return config


async def main():
    config = load_config(config_default)
    setup_logging(config.LOGGING_LEVEL)
    logger.debug(
        "API configuration settings: \n%s",
        "\n".join(
            [
                "=".join([key, getattr(config, key)])
                for key in dir(config)
                if key.isupper()
            ]
        ),
    )

    app = create_app(config)

    await asyncio.gather(
        faiss_init(app),
        web._run_app(app),
    )


if __name__ == "__main__":
    asyncio.run(main())
