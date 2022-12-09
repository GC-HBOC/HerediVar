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

basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data_dir = basepath + "/data"



def test_user_lists(test_client):
    """
    This first creates a new user list for the testuser and subsequentially adds variants, deletes, renames and searches them
    """
    
    ##### test that endpoint is reachable & no lists contained #####
    response = test_client.get(url_for("user.my_lists"), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert data.count('name="user_list_row"') == 2
    assert 'Please select a list to view its content!' in data


    ##### create a new list #####
    response = test_client.post(
        url_for("user.my_lists", type='create'), 
        data={
            "list_name": "first list"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))



    assert response.status_code == 200
    assert 'Successfully created new list' in data


    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 3
    list_id = conn.get_latest_list_id()

    conn.close()


    ##### add variants to the list #####
    variant_id = 71
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    variant_id = 72
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    ##### test that the variants are in the list #####
    conn = Connection(['super_user'])

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 2
    assert '71' in variants_in_list
    assert '72' in variants_in_list

    conn.close()

    ##### test showing the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    print(data)
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 2
    assert data.count('variant_id="71"') == 1
    assert data.count('variant_id="72"') == 1

    ##### test searching the list #####
    response = test_client.get(url_for("user.my_lists", view=list_id, genes='BRCA1'), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200
    assert data.count('variant_id="') == 1
    assert data.count('variant_id="71"') == 1

    ##### test renaming the list #####
    response = test_client.post(
        url_for("user.my_lists", type='edit'), 
        data={
            "list_name": "first list update",
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully changed list settings' in data
    
    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 3
    assert conn.get_user_variant_list(list_id)[2] == "first list update"

    conn.close()


    ##### test deleting variants from the list #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=71), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed variant from list!' in data

    conn = Connection(['super_user'])

    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 1
    assert '72' in variants_in_list

    conn.close()
    
    ##### test deleting the list #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_list'), 
        data={
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed list' in data

    conn = Connection(['super_user'])

    user_lists = conn.get_lists_for_user(session['user']['user_id'])
    assert len(user_lists) == 2

    conn.close()


    ##### test accessing the private list from another user #####
    response = test_client.get(url_for("user.my_lists", view=10), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403


    ##### test accessing the public list from another user #####
    response = test_client.get(url_for("user.my_lists", view=8), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200


    ##### test accessing the public&editable list from another user #####
    response = test_client.get(url_for("user.my_lists", view=9), follow_redirects=True)
    data = html.unescape(response.data.decode('utf8'))
    
    assert response.status_code == 200


    ##### test deleting the public list from another user #####
    response = test_client.post(
        url_for("user.my_lists", type='delete_list'), 
        data={
            "list_id": 9
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403

    ##### test adding variants to the public list from another user #####
    list_id = 9 # public read & edit -> should work
    variant_id = 71
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 200

    conn = Connection(['super_user'])
    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 1
    assert '71' in variants_in_list
    conn.close()

    list_id = 8 # only public read -> should not work
    response = test_client.post(
        url_for("user.modify_list_content", variant_id=variant_id, action='add_to_list', selected_list_id=list_id),
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))
    assert response.status_code == 403

    ##### test renaming & changing the permission bits a public list from another user #####
    list_id = 9
    response = test_client.post(
        url_for("user.my_lists", type='edit'), 
        data={
            "list_name": "first list update",
            "list_id": list_id
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403

    ##### test deleting variants from the public list #####
    list_id = 9 # should work
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=71), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully removed variant from list!' in data

    conn = Connection(['super_user'])
    variants_in_list = conn.get_variant_ids_from_list(list_id)
    assert len(variants_in_list) == 0
    conn.close()

    list_id = 8 # should not work
    response = test_client.post(
        url_for("user.my_lists", type='delete_variant', view=list_id, variant_id=52), 
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 403


    ##### test creating a public list #####
    response = test_client.post(
        url_for("user.my_lists", type='create'), 
        data={
            "list_name": "new public list",
            "public_read": "true",
            "public_edit": "true"
        },
        follow_redirects=True
    )
    data = html.unescape(response.data.decode('utf8'))

    assert response.status_code == 200
    assert 'Successfully created new list' in data

    # check that the public and private bits are set correctly
    conn = Connection(['super_user'])
    public_list_id = conn.get_latest_list_id()
    list_oi = conn.get_user_variant_list(public_list_id)
    assert list_oi[3] == 1
    assert list_oi[4] == 1
    conn.close()

