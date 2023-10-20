import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
import json



def insert_criterium_scheme(conn: Connection, data):
    classification_scheme_id = conn.insert_criterium_scheme(
        classification_scheme_id = data.get("classification_scheme_id", ""),
        name = data["name"],
        display_name = data["display_name"],
        scheme_type = data["type"],
        reference = data["reference"]
    )
    return classification_scheme_id


def insert_criteria(conn: Connection, data, classification_scheme_id):
    criteria = data["criteria"]

    criterium_name_to_criterium_id = {}

    for criterium in criteria:
        criterium_id = conn.insert_criterium(
            classification_scheme_id = classification_scheme_id,
            name = criterium["name"],
            description = '\n'.join(criterium["description"]),
            is_selectable = criterium["is_selectable"],
            relevant_info = criterium["relevant_info"]
        )
        criterium_name_to_criterium_id[criterium["name"]] = criterium_id

        for criterium_strength in criterium["strengths"]:
            conn.insert_criterium_strength(
                criterium_id = criterium_id,
                name = criterium_strength["name"],
                description = criterium_strength["description"],
                is_default = criterium_strength["is_default"]
            )

    for criterium in criteria:
        source_id = conn.get_classification_criterium_id(classification_scheme_id, criterium['name'])
        conn.delete_mutually_exclusive_criteria(source_id)
        for mutually_exclusive_criterium in criterium["mutually_exclusive_criteria"]:
            source = criterium_name_to_criterium_id.get(criterium["name"])
            target = criterium_name_to_criterium_id.get(mutually_exclusive_criterium)
            if source is not None and target is not None:
                conn.insert_mutually_exclusive_criterium(
                    source = source,
                    target = target
                )


def delete_criteria(conn: Connection, data, classification_scheme_id):
    criteria = data["criteria"]
    new_criteria_names = [x['name'] for x in criteria]

    schemas = conn.get_classification_schemas()
    scheme_oi = schemas[int(classification_scheme_id)]

    for db_criterium_name in scheme_oi["criteria"]:
        if db_criterium_name not in new_criteria_names:
            conn.delete_criterium(classification_scheme_id, db_criterium_name)
            continue
            
        db_criterium_strengths = scheme_oi["criteria"][db_criterium_name]['possible_strengths']
        criterium = get_criterium(criteria, db_criterium_name)
        if criterium is not None:
            new_criterium_strengths = [x['name'] for x in criterium['strengths']]
            for db_criterium_strength in db_criterium_strengths:
                if db_criterium_strength not in new_criterium_strengths:
                    criterium_id = conn.get_classification_criterium_id(classification_scheme_id, db_criterium_name)
                    conn.delete_criterium_strength(criterium_id, db_criterium_strength)


def get_criterium(all_criteria, criterium_name):
    for criterium in all_criteria:
        if criterium['name'] == criterium_name:
            return criterium
    return None

if __name__ == "__main__":

    conn = Connection(roles = ['super_user'])

    data = json.loads(open("/mnt/storage2/users/ahdoebm1/HerediVar/resources/classification_schemes/ClinGen_BRCA1_v1.0.0.json").read())
    
    """
    data = {
        'classification_scheme_id': "10", # leave blank to specify new scheme or provide id to specify an update
        'name': "testscheme",
        'display_name': "yoyotest",
        'type': "acmg",
        'reference': "#",
        'criteria': [ # compute classification_scheme_id
            {
                "name": "PSVS1", # has to be unique because of the mutually exclusive criteria list
                "description": "THIS IS A TEST",
                "is_selectable": "1",
                "relevant_info": "",
                "strengths": [ # compute classification_criterium_id
                    {
                        'name': "pvs",
                        'description': "pathogenic very strong",
                        'is_default': "1"
                    },
                    {
                        'name': "ps",
                        'description': "pathogenic strong",
                        'is_default': "0"
                    }
                ],
                "mutually_exclusive_criteria": [ # list of criterium names
                    "PS1"
                ]
            },

            {
                "name": "PS1", # has to be unique because of the mutually exclusive criteria list
                "description": "ps1 test yoo",
                "is_selectable": "1",
                "relevant_info": "",
                "strengths": [ # compute classification_criterium_id
                    {
                        'name': "ps",
                        'description': "pathogenic strong",
                        'is_default': "1"
                    }
                ],
                "mutually_exclusive_criteria": [ # list of criterium names
                    
                ]
            },
        ]
    }
    """

    classification_scheme_id = insert_criterium_scheme(conn, data)
    insert_criteria(conn, data, classification_scheme_id)
    delete_criteria(conn, data, classification_scheme_id)



















