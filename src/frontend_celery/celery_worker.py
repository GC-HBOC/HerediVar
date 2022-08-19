
import os
from webapp import create_app

env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())
app.app_context().push()

from webapp import celery