
import os
from webapp import create_app

app = create_app()
app.app_context().push()

from webapp import celery