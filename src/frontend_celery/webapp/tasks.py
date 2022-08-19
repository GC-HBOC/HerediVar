from urllib.error import HTTPError
from . import celery
#import sys
#from os import path
#sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
#import common.functions as functions
#from common.db_IO import Connection
from annotation_service.main import process_one_request
from celery.exceptions import Ignore

"""
@celery.task(bind=True)
def long_task(self):
    #Background task that runs a long function with progress reports.
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 20)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        #time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task(bind=True)
def fetch_consequence_task(self, variant_id):
    #Background task for fetching the consequence from the database
    self.update_state(state='PROGRESS')
    
    conn = Connection()

    time.sleep(10)
    variant_consequences = conn.get_variant_consequences(variant_id) # 0transcript_name,1hgvs_c,2hgvs_p,3consequence,4impact,5exon_nr,6intron_nr,7symbol,8transcript.gene_id,9source,10pfam_accession,11pfam_description,12length,13is_gencode_basic,14is_mane_select,15is_mane_plus_clinical,16is_ensembl_canonical,17total_flag
    conn.close()
    return {'status': 'COMPLETED', 'result': variant_consequences}
"""


# this uses exponential backoff in case there is a http error
# this will retry 3 times before giving up
# first retry after 5 seconds, second after 25 seconds, third after 125 seconds (if task queue is empty that is)
@celery.task(bind=True, retry_backoff=5, max_retries=3)
def annotate_variant(self, annotation_queue_id):
    """Background task for running the annotation service"""
    self.update_state(state='PROGRESS', meta={'annotation_queue_id':annotation_queue_id})
    status, runtime_error = process_one_request(annotation_queue_id)
    if status == 'error':
        status = 'FAILURE'
        self.update_state(state=status, meta={'annotation_queue_id':annotation_queue_id, 
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded a runtime error: " + runtime_error, 
                        'custom': '...'
                    })
        raise Ignore()
    if status == "retry":
        status = "RETRY"
        self.update_state(state=status, meta={'annotation_queue_id':annotation_queue_id,
                        'exc_type': "Runtime error",
                        'exc_message': "The annotation service yielded " + runtime_error + "! Will attempt retry.", 
                        'custom': '...'})
        annotate_variant.retry()
    self.update_state(state=status, meta={'annotation_queue_id':annotation_queue_id})
