
from wsgiref.headers import Headers
from ._job import Job
import common.paths as paths
import common.functions as functions
import os
import requests
import urllib.parse
from ..pubmed_parser import fetch

## annotate variant with literature from litvar2: https://www.ncbi.nlm.nih.gov/research/litvar2/
class litvar2_job(Job):
    def __init__(self, job_config):
        self.job_name = "litvar2 annotation"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        litvar_code = 0
        litvar_stderr = ""
        litvar_stdout = ""
        if not self.job_config['do_litvar']:
            return litvar_code, litvar_stderr, litvar_stdout

        self.print_executing()

        
        #litvar_code, litvar_stderr, litvar_stdout = self.annotate_litvar(inpath, annotated_inpath)


        #self.handle_result(inpath, annotated_inpath, litvar_code)
        return litvar_code, litvar_stderr, litvar_stdout


    def save_to_db(self, info, variant_id, conn):
        rsid_annotation_type_id = conn.get_most_recent_annotation_type_id("rsid")
        litvar_pmids = None

        rsid = conn.get_variant_annotation(variant_id, rsid_annotation_type_id)
        if rsid is not None:
            rsid = "rs" + str(rsid[0][3])
            litvar_pmids = self.query_litvar(rsid)
            if litvar_pmids is None:
                rsid = None # hack to trigger search using hgvs if rsid did not yield a result


        if rsid is None:
            consequences = conn.get_variant_consequences(variant_id)
            if consequences is not None:
                consequences = conn.order_consequences(consequences)
                for consequence in consequences: # search for the first consequence which has a litvar response in order of preferred transcript
                    gene = consequence[7]
                    hgvs = consequence[1] # hgvsc
                    if hgvs is None: # no hgvsc -> skip
                        continue

                    litvar_query = gene + " " + hgvs
                    litvar_pmids = self.query_litvar(litvar_query)
                    if litvar_pmids is not None:
                        break
        
        #print(litvar_pmids)
        if litvar_pmids is not None and self.job_config['insert_literature']:
            literature_entries = fetch(litvar_pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "litvar")
    
    def query_litvar(self, query):
        # get litvar id from data
        #BARD1%20c.1972C%3ET
        query = urllib.parse.quote(str(query))
        url = "https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/autocomplete/?query=" + query
        resp = requests.get(url)
        data = resp.json()
        litvar_id = data[0].get('_id')
        if litvar_id is None:
            return None

        litvar_id = urllib.parse.quote(str(litvar_id))
        url = "https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/get/" + litvar_id + "/publications"
        #print(url)
        resp = requests.get(url)
        data = resp.json()

        pmids_litvar = None
        if 'pmids' in data:
            if data['pmids'] != '':
                pmids_litvar = ','.join([str(x) for x in data['pmids']])

        return pmids_litvar


