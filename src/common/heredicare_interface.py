
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common.functions as functions
from common.xml_validator import xml_validator
from common.singleton import Singleton
from datetime import datetime, timedelta
import re
import json
import urllib

#class Heredicare_Flask():
#    def __init__(self, app=None):
#        self.app = app
#        if app is not None:
#            self.state = self.init_app(app)
#        else:
#            self.state = None
#
#    def init_app(self, app):
#        state = Heredicare()
#
#        # register extension with app
#        app.extensions = getattr(app, 'extensions', {})
#        app.extensions['heredicare'] = state
#        return state
#
#    def __getattr__(self, name):
#        return getattr(self.state, name, None)




class Heredicare(metaclass=Singleton):
    bearer = {}
    bearer_timestamp = {}

    def __init__(self):
        self.base_url = "https://hazel.imise.uni-leipzig.de/pids2" # /project
        self.projects = {
            "download": os.environ.get("HEREDICARE_DOWNLOAD_PROJECT"),
            "upload": os.environ.get("HEREDICARE_UPLOAD_PROJECT")
        }
        self.endpoints = {
            # special endpoints
            "bearer": "oauth/token",

            # download endpoints
            "vid_list": "vars/list",
            "variant": "vars/get",
            "var_info": "vars/info",

            # upload endpoints
            "post_info": "vars/send/info",
            "submissionid": "submissionid/get",
            "send_data": "vars/send/",
            "submission_status": "vars/send/result",
            "recordid": "recordid/get"
        }
        #print("NEW INSTANCE")

    # path arguments must be in the correct order
    def get_url(self, project_type, endpoint, path_args = []): 
        url = self.base_url + "/" + self.projects[project_type] + "/" + self.endpoints[endpoint]
        if len(path_args) > 0:
            url += "/" + "/".join(path_args)
        #print(url)
        return url

    def get_auth(self, project_type):
        if project_type == "download":
            auth = (os.environ.get("HEREDICARE_DOWNLOAD_CLIENT_ID"), os.environ.get("HEREDICARE_DOWNLOAD_CLIENT_PASSWORD"))
        elif project_type == "upload":
            auth = (os.environ.get("HEREDICARE_UPLOAD_CLIENT_ID"), os.environ.get("HEREDICARE_UPLOAD_CLIENT_PASSWORD"))
        return auth
    
    def get_saved_bearer(self, project_type):
        project = self.projects[project_type]
        return self.bearer.get(project), self.bearer_timestamp.get(project, datetime.now())

    def get_bearer(self, project_type): # project_type is either "upload" or "download"
        message = ""
        bearer = None
        status = "success"
        url = self.get_url(project_type, "bearer")
        auth = self.get_auth(project_type)
        data = {"grant_type":"client_credentials"}
        if any([x is None for x in auth]): # bearer is none
            message = "ERROR: missing credentials for HerediCare API!"
            status = "error"
        else:
            resp = requests.post(url, auth=auth, data=data)
            if resp.status_code != 200: # bearer is None
                message = "ERROR: HerediCare API client credentials endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
                status = "error"
            else:
                bearer = resp.json()["access_token"]
        return bearer, status, message

    def extract_error_message(self, error_text):
        result = error_text
        cropped_text = functions.find_between(error_text, prefix="<div id=\"reasons\"", postfix="(</div>|$)")
        if cropped_text is not None:
            result = cropped_text
        else:
            cropped_text = functions.find_between(error_text, prefix="<title>", postfix="</title>")
            if cropped_text is not None:
                result = cropped_text
        return result


    def update_token(self, timestamp, project_type):
        new_bearer, status, message = self.get_bearer(project_type)
        if status == 'success':
            project = self.projects[project_type]
            Heredicare.bearer[project] = new_bearer
            Heredicare.bearer_timestamp[project] = timestamp
            print("UPDATED TOKEN!!!!")
        return status, message

    def introspect_token(self, project_type):
        now = datetime.now()
        status = "success"
        message = ""
        #print("TOKEN: " + str(self.bearer))
        bearer, timestamp = self.get_saved_bearer(project_type)
        if bearer is None:
            status, message = self.update_token(now, project_type)
        elif timestamp + timedelta(minutes = 50) <= now:
            status, message = self.update_token(now, project_type)
        return status, message


    def get_vid_list(self):
        status = "success"
        message = ""
        vids = []
        project_type = "download"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return vids, status, message

        url = self.get_url(project_type, "vid_list")
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get vid list endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code != 200: # any other kind of error
            message = "ERROR: HerediCare API get vid list endpoint returned an HTTP " + str(resp.status_code) + " error: " + + self.extract_error_message(resp.text)
            status = "error"
        else: # request was successful
            vids = resp.json()['items']

        return vids, status, message
    
    def filter_vid_list(self, vids, min_date):
        all_vids = []
        filtered_vids = []
        duplicate_vids = []
        status = "success"
        message = ""

        for vid_raw in vids:
            current_vid = str(vid_raw['record_id'])
            last_change = vid_raw['last_change']
            last_change = datetime.strptime(last_change, '%d.%m.%Y %H:%M:%S')
            if current_vid in filtered_vids:
                duplicate_vids.append(current_vid)
            if min_date is None or (last_change > min_date): # collect all which had an update since the last import
                filtered_vids.append(current_vid)
            all_vids.append(current_vid)

        if len(duplicate_vids) > 0:
            message = "WARNING: There are duplicated VIDs in the response of the variant list output: " + str(duplicate_vids)
        
        return filtered_vids, all_vids, status, message
    

    def get_variant(self, vid):
        status = "success"
        message = ""
        variant = None
        project_type = "download"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return variant, status, message

        url = self.get_url(project_type, "variant", path_args = [str(vid)])
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get variant endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API get variant endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "error"
        else: # success
            raw_variant = resp.json()
            variant = self.convert_heredicare_variant_raw(raw_variant)
        
        return variant, status, message

    
    def convert_heredicare_variant_raw(self, raw_variant):
        variant = {}
        for item in raw_variant['items']:
            item_name = item['item_name']
            item_value = item['item_value']
            variant[item_name] = item_value
        return variant


    def get_post_regexes(self):
        status = "success"
        message = ""
        all_items = []
        project_type = "upload"

        url = self.get_url(project_type, "post_info") # first url
        has_next = True
        
        while has_next:
            status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
            if status == 'error':
                return [], status, message
            bearer, timestamp = self.get_saved_bearer(project_type)
            header = {"Authorization": "Bearer " + bearer}
            resp = requests.get(url, headers=header)
            if resp.status_code == 401: # unauthorized
                message = "ERROR: HerediCare API get post info endpoint returned an HTTP 401, unauthorized error. Attempting retry."
                status = "retry"
                break
            elif resp.status_code != 200: # any other kind of error
                message = "ERROR: HerediCare API get post info endpoint returned an HTTP " + str(resp.status_code) + " error: " + + self.extract_error_message(resp.text)
                status = "error"
                break
            else: # request was successful
                resp = resp.json()
                new_items = resp["items"]
                all_items.extend(new_items)
                has_next = resp["hasMore"]
                for link in resp["links"]:
                    if link["rel"] == "next":
                        url = link["href"]

        #with open("/mnt/storage2/users/ahdoebm1/HerediVar/src/common/test.json", "w") as f:
        #    functions.prettyprint_json(all_items, func = f.write)

        result = {}
        for item in all_items:
            item_name = item["item_name"]
            regex = item["item_regex_format"]
            #if item_name == "PATH_TF":
            #    regex = r"^(-1|[1-4]|1[1-5]|2[01]|32|34)$"
            #elif item_name == "VUSTF_DATUM":
            #    regex = r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[012])\.20\d\d$"
            result[item_name] = regex

        return result, status, message

    def get_new_submission_id(self):
        status = "success"
        message = ""
        submission_id = None
        project_type = "upload"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return submission_id, status, message

        url = self.get_url(project_type, "submissionid")
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get submission id endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API getsubmission id endpoint endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "error"
        else: # success
            submission_id = resp.json()["items"][0]["submission_id"]
            
        return submission_id, status, message
    
    def get_new_record_id(self):
        status = "success"
        message = ""
        record_id = None
        project_type = "upload"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return record_id, status, message

        url = self.get_url(project_type, "recordid")
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get submission id endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API getsubmission id endpoint endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "error"
        else: # success
            record_id = resp.json()["items"][0]["record_id"]

        return record_id, status, message

    def get_submission_status(self, submission_id):
        status = "success"
        message = ""
        finished_at = None
        project_type = "upload"

        if submission_id is None:
            status = "pending"
            return finished_at, status, message

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'api_error':
            return finished_at, status, message

        url = self.get_url(project_type, "submission_status", [str(submission_id)])
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code != 200:
            message = "ERROR: HerediCare API getsubmission id endpoint endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "api_error"
        else: # success
            resp = resp.json(strict=False)
            items = resp["items"]
            
            if len(items) == 0: # submission id was generated but no data was posted yet
                status = "pending"
            else:
                info = items[0]
                process_result = info["process_result"]
                process_date = info["process_date"]

                if process_date != "":
                    finished_at = functions.reformat_date(process_date, input_pattern = "%d.%m.%y", output_pattern = "%Y-%m-%d") # "08.05.24"

                if process_result == "noch nicht verarbeitet":
                    status = "submitted"
                elif process_result == "Import OK":
                    status = "success"
                else:
                    status = "error"
                    message = str(process_result)

        return finished_at, status, message

    def get_variant_items(self, variant, vid, submission_id, post_regexes, transaction_type):
        status = "success"
        message = ""
        all_items = []

        heredicare_variant = {}
        if transaction_type == 'UPDATE':
            heredicare_variant, status, message = self.get_variant(vid)
            if status == 'error':
                return all_items, status, message

        #print(heredicare_variant)
        #mandatory update 
        #Item fehlt für UPDATE: CHROM
        item_name = "CHROM"
        item_regex = post_regexes[item_name]
        new_value = functions.trim_chr(variant.chrom)
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = functions.trim_chr(variant.chrom) if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)
        #Item fehlt für UPDATE: POS_HG38
        item_name = "POS_HG38"
        item_regex = post_regexes[item_name]
        new_value = str(variant.pos)
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = str(variant.pos) if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)
        #Item fehlt für UPDATE: REF_HG38
        item_name = "REF_HG38"
        item_regex = post_regexes[item_name]
        new_value = variant.ref
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = variant.ref if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)
        #Item fehlt für UPDATE: ALT_HG38
        item_name = "ALT_HG38"
        item_regex = post_regexes[item_name]
        new_value = variant.alt
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = variant.alt if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)


        preferred_consequence = None
        if transaction_type == 'INSERT':
            preferred_gene = variant.get_genes('best')
            if preferred_gene is not None:
                preferred_consequences = variant.get_preferred_transcripts()
                if preferred_consequences is not None:
                    for consequence in preferred_consequences:
                        if consequence.transcript.gene.symbol == preferred_gene:
                            preferred_consequence = consequence
                            break

        preferred_gene = preferred_consequence.transcript.gene.symbol if preferred_consequence is not None else None
        preferred_transcript = preferred_consequence.transcript.name if preferred_consequence is not None else None

        #Item fehlt für UPDATE: GEN
        item_name = "GEN"
        item_regex = post_regexes[item_name]
        new_value = heredicare_variant["GEN"] if transaction_type == 'UPDATE' else preferred_gene
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = heredicare_variant["GEN"] if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)
        #Item fehlt für UPDATE: REFSEQ
        item_name = "REFSEQ"
        item_regex = post_regexes[item_name]
        new_value = heredicare_variant["REFSEQ"]  if transaction_type == 'UPDATE' else preferred_transcript
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = heredicare_variant["REFSEQ"] if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        # mandatory insert
        #KONS_VCF
        if transaction_type == 'INSERT':
            item_name = "KONS_VCF"
            item_regex = post_regexes[item_name]
            new_value = preferred_consequence.consequence if preferred_consequence is not None else None
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return all_items, status, message
            old_value = None
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)
        #CHGVS
            item_name = "CHGVS"
            item_regex = post_regexes[item_name]
            new_value = preferred_consequence.hgvs_c if preferred_consequence is not None else None
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return all_items, status, message
            old_value = None
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)
        #PHGVS
            item_name = "PHGVS"
            item_regex = post_regexes[item_name]
            new_value = preferred_consequence.hgvs_p if preferred_consequence is not None else None
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return all_items, status, message
            old_value = None
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)

        return all_items, status, message



    def get_consensus_classification_items(self, variant, vid, submission_id, post_regexes):
        status = "success"
        message = ""
        all_items = []
        mrcc = variant.get_recent_consensus_classification()

        # some sanity checks - maybe not neccessary, but its not bad to check those beforehand
        if mrcc is None or mrcc.selected_class is None or mrcc.selected_class == "-":
            status =  "skipped"
            message = "The variant does not have a consensus classification which can be submitted"
            return all_items, status, message
        elif not mrcc.needs_heredicare_upload: # skip if the consensus classification was already uploaded
            status = "skipped"
            message = "The consensus classification is already uploaded to HerediCaRe."
            return all_items, status, message
        
        # add consensus classification class in HerediCare format: PATH_TF
        item_name = "PATH_TF"
        item_regex = post_regexes[item_name]
        new_value = functions.num2heredicare(mrcc.selected_class, single_value=True)
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = self.get_heredicare_consensus_attribute(variant, vid, "selected_class")
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        # add date of consensus classification: VUSTF_DATUM
        item_name = "VUSTF_DATUM"
        item_regex = post_regexes[item_name]
        new_value = functions.reformat_date(mrcc.date, '%Y-%m-%d %H:%M:%S', '%d.%m.%Y')
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = self.get_heredicare_consensus_attribute(variant, vid, "classification_date")
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        # add comment of consensus classification: VUSTF_17
        item_name = "VUSTF_17"
        item_regex = post_regexes[item_name]
        new_value = mrcc.get_extended_comment()
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = self.get_heredicare_consensus_attribute(variant, vid, "comment")
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        ##Item fehlt für UPDATE: VUSTF_16

        return all_items, status, message


    def is_valid_post_data(self, value, regex):
        pattern = re.compile(regex)
        result = pattern.match(value)
        if result is None:
            return False
        return True

    def get_heredicare_consensus_attribute(self, variant, vid, attribute_name):
        heredicare_annotation = variant.get_heredicare_annotation_by_vid(vid)
        if heredicare_annotation is None:
            return None
        return getattr(heredicare_annotation.consensus_classification, attribute_name)

    def get_postable_item(self, record_id, submission_id, item_name, old_value, new_value):
        new_item = {
            "record_id": record_id,
            "submission_id": submission_id,
            "item_name": item_name,
            "item_value_old": old_value,
            "item_value_new": new_value
        }
        return new_item

    def get_terminating_item(self, record_id, submission_id, transaction_type):
        return {
            "record_id": record_id,
            "submission_id": submission_id,
            "item_name": "RECORD_COMPLETE",
            "item_value_old": "",
            "item_value_new": transaction_type
        }



    def get_data(self, variant, vid, options):
        status = "success"
        message = ""
        data = None
        submission_id = None

        post_regexes, status, message = self.get_post_regexes()
        if status == "error":
            return data, vid, submission_id, status, message
        
        transaction_type = "UPDATE"
        if vid is None:
            transaction_type = "INSERT"

        all_items = []

        # add basic information about the variant
        variant_items, status, message = self.get_variant_items(variant, vid, submission_id, post_regexes, transaction_type)
        if status in ['error', 'skipped']:
            return data, vid, submission_id, status, message
        all_items.extend(variant_items)

        # add the consensus classification
        if options['post_consensus_classification']:
            consensus_classification_items, status, message = self.get_consensus_classification_items(variant, vid, submission_id, post_regexes)
            if status in ["error", "skipped"]:
                return data, vid, submission_id, status, message
            all_items.extend(consensus_classification_items)

        # add terminating item
        all_items.append(self.get_terminating_item(record_id = vid, submission_id = submission_id, transaction_type = transaction_type))

        # get submission_id and record_id aka vid and update all items accordingly
        # It is good to add this information afterwards because we would generate a new record/submission id if the status of the data collection process is error or skipped (in case there is not enough data for submission)
        if transaction_type == "INSERT":
            vid, status, message = self.get_new_record_id()
            if status == 'error':
                return data, vid, submission_id, status, message
        submission_id, status, message = self.get_new_submission_id()
        if status == 'error':
            return data, vid, submission_id, status, message
        for i in range(len(all_items)):
            all_items[i]["record_id"] = vid
            all_items[i]["submission_id"] = submission_id
        
        # tinker all items together
        data = {'items': all_items}
        #with open('/mnt/storage2/users/ahdoebm1/HerediVar/src/common/heredicare_interface_debug/test.json', "w") as f:
        #    functions.prettyprint_json(data, f.write)
        data = json.dumps(data)

        return data, vid, submission_id, status, message


    def _post_data(self, data):
        status = "success"
        message = ""
        project_type = "upload"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return status, message        

        url = self.get_url(project_type, "send_data")
        bearer, timestamp = self.get_saved_bearer(project_type)
        header = {"Authorization": "Bearer " + bearer}
        resp = requests.post(url, headers=header, data=data)

        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API post variant data endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code == 555:
            message = "ERROR: HerediCare API post variant data endpoint returned an HTTP 555 error. Reason: " + urllib.parse.unquote(resp.headers.get("Error-Reason", "not provided"))
            status = "error"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API post variant data endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "error"
        else: # success
            print(resp.text)

        return status, message

    def post(self, variant, vid, options):
        status = "success"
        message = ""

        data, vid, submission_id, status, message = self.get_data(variant, vid, options)
        if status in ["error", "skipped"]:
            return vid, submission_id, status, message
        
        status, message = self._post_data(data)

        return vid, submission_id, status, message

        


if __name__ == "__main__":
    functions.read_dotenv()
    heredicare_interface = Heredicare()

    variant_id_oi = "55"

    from common.db_IO import Connection
    conn = Connection(roles = ["db_admin"])
    variant = conn.get_variant(variant_id_oi)
    conn.close()

    #submission_id, status, message = heredicare_interface.upload_consensus_classification(variant)
    #print(submission_id)
    #print(status)
    #print(message)

    #finished_at, status, message = heredicare_interface.get_submission_status(submission_id)
    #print(finished_at)
    #print(status)
    #print(message)


    #submission_id, status, message = heredicare_interface.get_new_submission_id()
    #print(submission_id)
    #print(status)
    #print(message)
    #finished_at, status, message = heredicare_interface.get_submission_status(submission_id)
    #print(finished_at)
    #print(status)
    #print(message)

    # 122: first success!
    finished_at, status, message = heredicare_interface.get_submission_status(122)
    print(finished_at)
    print(status)
    print(message)

    #
    heredicare_interface.get_data(variant, vid = "8882909", options = {"post_consensus_classification": True})

#if __name__ == "__main__":
#    functions.read_dotenv()
#
#    vids, status, message = heredicare_interface.get_vid_list()
#
#    for vid_raw in vids:
#        vid = vid_raw['record_id']
#        variant, status, message = heredicare_interface.get_variant(vid)
#
#        if variant["PATH_TF"] != "-1":
#            print(variant)
#            break

    


"""
{
GENERELLE INFORMATIONEN ÜBER DIE VARIANTE:
 'VID': '19439917' --> variant id
 'REV_STAT': '2' --> 2: kein review, 3: review erfolgt, 1: neu angelegt?
 'QUELLE': '2' --> 1: manuell, 2: upload
 'GEN': 'MSH2' --> das gen
 'REFSEQ': 'NM_000251.3' --> Transkript
 'ART': '-1' --> 1-6 sind klar, was bedeutet -1?
 'CHROM': '2' --> chromosom
 'POS_HG19': '47630514' --> hg19 position
 'REF_HG19': 'G' --> hg19 reference base
 'ALT_HG19': 'C' --> hg19 alternative base
 'POS_HG38': '47403375' --> hg38 position
 'REF_HG38': 'G' --> hg38 reference base
 'ALT_HG38': 'C' --> hg38 alternative base
 'KONS': '-1' --> consequence, value 1-10
 'KONS_VCF': 'missense_variant' --> consequence?? was ist der Unterschied zu KONS?
 'CHGVS': 'c.184G>C' --> c.hgvs
 'PHGVS': 'Gly62Arg' --> p.hgvs

 'CBIC': None --> ??
 'PBIC': None --> ??
 'CGCHBOC': None --> ??
 'PGCHBOC': None --> ??

TF CONSENSUS KLASSIFIKATION:
 'PATH_TF': '-1' --> Klassifikation der task-force: Fragen: wofür werden die Werte 1-3 verwendet?, Was ist der Wert 20 (Artefakt)?, Was ist der Unterschied zwischen den Werten -1, 21 und 4?
 'BEMERK': None --> Das Kommentar der task-force zur Klassifikation
 'VUSTF_DATUM': None --> Datum der task-force Klassifikation
 'VUSTF_01': None --> annotation
 'VUSTF_02': None --> annotation
 'VUSTF_03': None --> annotation
 'VUSTF_04': None --> annotation
 'VUSTF_05': None --> annotation
 'VUSTF_06': None --> annotation
 'VUSTF_07': None --> annotation
 'VUSTF_08': None --> annotation
 'VUSTF_09': None --> annotation
 'VUSTF_10': None --> annotation
 'VUSTF_11': None --> annotation
 'VUSTF_12': None --> annotation
 'VUSTF_13': None --> annotation
 'VUSTF_14': None --> annotation
 'VUSTF_15': None --> annotation - literatur -> wichtig?
 'VUSTF_16': None --> annotation - evidenzlevel literatur -> wichtig?
 'VUSTF_17': None --> annotation - kommentar -> wichtig?
 'VUSTF_18': None --> annotation
 'VUSTF_BEMERK': None --> wo liegt hier der Unterschied zu BEMERK?
 'ERFDAT': '23.09.2023' --> Datum an dem die Variante hochgeladen wurde?
 'VISIBLE': '1' --> Ignoriere Varianten mit 0?
 'VID_REMAP': None --> Hat was mit VISIBLE zu tun. Wenn sie nicht visible ist dann ist es ein duplikat und wurde remapped auf die vid die dann hier steht?
 'N_PAT': '1' --> Anzahl der Fälle mit dieser Variante?
 'N_FAM': '1' --> Anzahl der Familien mit dieser Variante?
}

"""