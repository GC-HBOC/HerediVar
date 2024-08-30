from os import path
import sys
from upload import upload_tasks
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from common.db_IO import Connection


if __name__ == "__main__":
    variant_id = 55
    upload_queue_id = None
    user_id = 2
    user_roles = ["db_admin"]
    conn = Connection(user_roles)
    upload_tasks.start_upload_one_variant_heredicare(variant_id, upload_queue_id, user_id, user_roles, conn)