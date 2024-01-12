
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

        if self.job_config['do_litvar']:
            self.print_executing()

        
        #litvar_code, litvar_stderr, litvar_stdout = self.annotate_litvar(inpath, annotated_inpath)


        #self.handle_result(inpath, annotated_inpath, litvar_code)
        return litvar_code, litvar_stderr, litvar_stdout


    def save_to_db(self, info, variant_id, conn):
        status_code = 0
        err_msg = ""
        if not self.job_config['do_litvar']:
            return status_code, err_msg
        
        variant = conn.get_variant(variant_id, 
                    include_annotations = False, 
                    include_consensus = False, 
                    include_user_classifications = False, 
                    include_heredicare_classifications = False, 
                    include_automatic_classification = False,
                    include_clinvar = False, 
                    include_consequences = True, 
                    include_assays = False, 
                    include_literature = False,
                    include_external_ids = True
                )
        
        litvar_pmids = None

        rsids = variant.get_external_ids('rsid')
        if rsids is not None:
            for rsid in rsids:
                rsid = "rs" + str(rsid.strip('rs'))
                litvar_pmids = self.query_litvar(rsid)
                if litvar_pmids is not None:
                    break


        if litvar_pmids is None:
            consequences = variant.get_sorted_consequences()
            if consequences is not None:
                for consequence in consequences: # search for the first consequence which has a litvar response in order of preferred transcript
                    gene = consequence.transcript.gene.symbol
                    hgvs = consequence.hgvs_c # hgvsc
                    if hgvs is None or gene is None: # no hgvsc -> skip
                        continue
                    
                    litvar_query = gene + " " + hgvs
                    litvar_pmids = self.query_litvar(litvar_query)
                    if litvar_pmids is not None:
                        break
        
        if litvar_pmids is not None and self.job_config['insert_literature']:
            literature_entries = fetch(litvar_pmids) # defined in pubmed_parser.py
            for paper in literature_entries: #[pmid, article_title, authors, journal, year]
                conn.insert_variant_literature(variant_id, paper[0], paper[1], paper[2], paper[3], paper[4], "litvar")

        return status_code, err_msg
    
    def query_litvar(self, query):
        # get litvar id from data
        #BARD1%20c.1972C%3ET
        query = urllib.parse.quote(str(query))
        url = "https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/autocomplete/?query=" + query
        resp = requests.get(url)
        data = resp.json()

        if len(data) == 0:
            return None
        litvar_id = data[0].get('_id')
        if litvar_id is None:
            return None

        litvar_id = urllib.parse.quote(str(litvar_id))
        url = "https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/get/" + litvar_id + "/publications"
        resp = requests.get(url)
        data = resp.json()
        

        pmids_litvar = None
        if 'pmids' in data:
            if data['pmids'] != '':
                pmids_litvar = ','.join([str(x) for x in data['pmids']])

        return pmids_litvar


