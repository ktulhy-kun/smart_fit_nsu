import sys
import logging
logging.basicConfig(stream=sys.stderr)

from flaskr import app as application
application.secret_key = 'Secret'
