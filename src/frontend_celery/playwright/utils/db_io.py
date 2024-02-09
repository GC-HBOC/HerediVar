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

    #def revert_database(self):
    #    paths = ["/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_structure/structure.sql",
    #             "/mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/playwright/data/db_seeds/static.sql"]
    #    for path in paths:
    #        with open(path, 'r') as file:
    #            commands = file.read()
    #            iterator = self.cursor.execute(commands, multi=True)
    #            for i in iterator:
    #                self.conn.commit()

    def test(self):
        command = 'INSERT INTO user (username, first_name, last_name, affiliation) VALUES ("test", "firstname", "lastname", "affiliation"); INSERT INTO user (username, first_name, last_name, affiliation) VALUES ("test2", "firstname2", "lastname2", "affiliation2");'
        r = self.cursor.execute(command, multi=True)
        #self.conn.commit()
        assert False
