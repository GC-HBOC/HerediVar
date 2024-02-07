from os import path
import os
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import utils
import re
#from playwright.sync_api import Page, expect, sync_playwright
from flask import url_for
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
import common.functions as functions
from common.db_IO import Connection



class Test_Connection(Connection):

    def test(self):
        command = "SELECT * FROM user_variant_lists"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        print(result)
        assert False