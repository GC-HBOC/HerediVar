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

    def revert_database(self):
        command = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/revert_db.sh"]
        functions.execute_command(command, "mysql")
        #paths = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_structure/structure.sql",
        #         "/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_seeds/static.sql"]
        #for path in paths:
        #    command = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/revert_db.sh"]
        #    #command = ["mysql", "-h", os.environ.get("DB_HOST"), "-P", os.environ.get("DB_PORT"), "-u" + os.environ.get("DB_ADMIN"), "-p" + os.environ.get("DB_ADMIN_PW"), os.environ.get("DB_NAME"), path]
        #    functions.execute_command(command, "mysql")
        #    print(command)

    def test(self):
        command = "SELECT * FROM user_variant_lists"
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        print(result)
        assert False