import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - [%(name)s] - [%(levelname)-5s] - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {"handlers": ["default"]},  # root logger
        "aiohttp": {"handlers": ["default"], "propagate": False},
        "api": {"handlers": ["default"], "propagate": False},
        "__main__": {  # if __name__ == '__main__'
            "handlers": ["default"],
            "propagate": False,
        },
    },
}


def setup_logging(logging_level):
    """Setup chat logging

    Logging is configured based on `LOGGING_CONFIG` definition and
    global logging level from configuration file

    Args:
        logging_level (str): Global logging level

    """
    logging.config.dictConfig(LOGGING_CONFIG)
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if not logging.getLogger(name).level
    ]

    for logger in loggers:
        logger.setLevel(logging_level)
