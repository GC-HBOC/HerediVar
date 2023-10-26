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

def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links


def compare_vcf(reference_file, vcf_string):
    for line in reference_file:
        line = line.strip()
        if line == '':
            continue
        if line.startswith('#'): 
            if not line.startswith('##fileDate'): # skip the filedate header line because this one changes daily, but the test data is not updated daily
                assert line in vcf_string # test that header line is there
            continue

        parts = line.split('\t')
        info = parts[7]

        assert info[0:7].join('\t') in vcf_string # test that variant is there

        for info_entry in info.split(';'):
            print(info_entry)
            if 'consequences' in info_entry:
                for consequence in info_entry.strip('consequences=').split('&'):
                    assert consequence in vcf_string
            else:
                #if (info_entry not in vcf_string):
                #    print(info_entry)
                #    print(vcf_string)
                assert info_entry.strip() in vcf_string # test that info is there


