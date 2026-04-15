import os
import logging
import sys

# Configure a basic stderr handler before Django is loaded so these messages
# are always visible in deployment logs regardless of Django's logging setup.
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter('[WSGI] %(asctime)s %(levelname)s %(message)s'))
_logger = logging.getLogger('panaderia_backend.wsgi')
_logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG)

_logger.info('wsgi.py module is loading — setting DJANGO_SETTINGS_MODULE')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panaderia_backend.settings')

_logger.info('Calling get_wsgi_application() — Django app registry will now initialise')

try:
    application = get_wsgi_application()
    _logger.info('get_wsgi_application() returned successfully — application object is ready')
except Exception as exc:
    _logger.exception('get_wsgi_application() raised an exception: %s', exc)
    raise