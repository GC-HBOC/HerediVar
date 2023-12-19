from flask import request, url_for, session, current_app
from urllib.parse import urlparse
import requests
import html
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from common.db_IO import Connection
import re
from io import StringIO, BytesIO
import common.functions as functions
import time
import utils


basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = basepath + "/data"
