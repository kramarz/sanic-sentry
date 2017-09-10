import logging

import sanic

import raven
import raven_aiohttp
from raven.handlers.logging import SentryHandler
from raven.processors import Processor


class SanicSentry:
    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: sanic.Sanic):
        self.client = raven.Client(
            dsn=app.config['SENTRY_DSN'],
            transport=raven_aiohttp.AioHttpTransport,
        )
        self.handler = SentryHandler(client=self.client, level=app.config.get('SENTRY_LEVEL', logging.ERROR))
        logger = logging.getLogger('sanic')
        logger.addHandler(self.handler)
        self.app = app
        self.app.sentry = self


class RequestProcessor(Processor):
    async def process(self, data, request=None):
        if request is None:
            return {}

        data = {
            'request': {
                'url': "%s://%s%s" % (request.scheme, request.host, request.path),
                'method': request.method,
                'data': (await request.read()),
                'query_string': request.query_string,
                'headers': {k.title(): str(v) for k, v in request.headers.items()},
            }
        }

        return data