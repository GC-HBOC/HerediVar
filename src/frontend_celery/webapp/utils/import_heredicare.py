import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import common.paths as paths
import json
import argparse
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import upload.upload_functions as upload_functions
import frontend_celery.webapp.tasks as tasks


roles = ["db_admin"]

conn = Connection(roles)

# update state of unfinished heredicare uploads
variant_ids = conn.get_variant_ids_by_publish_heredicare_status(stati = ['pending', 'progress', 'submitted'])
upload_functions.check_update_all_most_recent_heredicare(variant_ids, conn)

# update state of unfinished clinar uploads
variant_ids = conn.get_variant_ids_by_publish_clinvar_status(stati = ['pending', 'progress', 'submitted'])
upload_functions.check_update_all_most_recent_clinvar(variant_ids, conn)


# import HerediCaRe VIDs
botname = "heredivar_bot"
conn.insert_user(username = botname, first_name = "HerediVar", last_name = "Bot", affiliation = "Bot", api_roles = "")
bot_id = conn.get_user_id(botname)
vids = "update" # start task importing all updated heredicare vids
import_queue_id = tasks.start_variant_import(vids, bot_id, roles, conn)

conn.close()
