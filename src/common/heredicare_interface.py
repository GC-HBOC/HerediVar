
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
import time

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

    max_tries = 3
    backoff_mult = 20

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
        
        auth = self.get_auth(project_type)
        if any([x is None for x in auth]): # bearer is none
            message = "ERROR: missing credentials for HerediCare API!"
            status = "error"
        else:
            retry = True
            current_try = 0

            while retry and (current_try <= self.max_tries):
                url = self.get_url(project_type, "bearer")
                data = {"grant_type":"client_credentials"}

                time.sleep(current_try * self.backoff_mult)
                resp = requests.post(url, auth=auth, data=data)

                if resp.status_code in [401, 503]: # unauthorized, service unavailable --> retry these
                    message = "ERROR: HerediCare API client credentials endpoint returned an HTTP "  + str(resp.status_code)
                    status = "error"
                    current_try += 1
                elif resp.status_code == 555:
                    message = "ERROR: HerediCare API client credentials endpoint returned an HTTP 555 error. Reason: " + urllib.parse.unquote(resp.headers.get("Error-Reason", "not provided"))
                    status = "error"
                    retry = False
                elif resp.status_code != 200:
                    message = "ERROR: HerediCare API client credentials endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
                    status = "error"
                    retry = False
                else: # success
                    status = "success"
                    message = ""
                    retry = False
                    bearer = resp.json()["access_token"]
                    #print(resp.text)

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
            #print("UPDATED TOKEN!!!!")
        return status, message

    def introspect_token(self, project_type):
        now = datetime.now()
        status = "success"
        message = ""
        bearer, timestamp = self.get_saved_bearer(project_type)
        if bearer is None:
            status, message = self.update_token(now, project_type)
        elif timestamp + timedelta(minutes = 50) <= now:
            status, message = self.update_token(now, project_type)
        return status, message


    def get_vid_list(self):
        status = "success"
        message = ""
        project_type = "download"

        url = self.get_url(project_type, "vid_list")
        status, message, all_vids = self.iterate_pagination(url, project_type)

        return all_vids, status, message
    
    
    def filter_vid_list(self, vids, min_date):
        filtered_vids = []
        duplicate_vids = []
        all_vids = []
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
        variant = {}
        project_type = "download"

        if vid is not None:
            url = self.get_url(project_type, "variant", path_args = [str(vid)])
            status, message, all_items = self.iterate_pagination(url, project_type)
            variant = self.convert_heredicare_variant_raw(all_items)

        return variant, status, message

    
    def convert_heredicare_variant_raw(self, variant_items):
        variant = {}
        for item in variant_items:
            item_name = item['item_name']
            item_value = item['item_value']
            variant[item_name] = item_value
        return variant

    def iterate_pagination(self, start_url, project_type, items_key = "items"):
        status = "success"
        message = ""
        result = []
        url = start_url
        has_next = True

        retry = True
        max_tries = 3
        backoff_mult = 20
        current_try = 0
        while has_next and retry and( current_try <= max_tries):
            status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
            if status == 'error':
                break
            bearer, timestamp = self.get_saved_bearer(project_type)
            header = {"Authorization": "Bearer " + bearer}
            time.sleep(current_try * backoff_mult)
            resp = requests.get(url, headers=header)
            if resp.status_code in [401, 503]: # unauthorized, service unavailable
                message = "ERROR: HerediCare API endpoint returned an HTTP " + str(resp.status_code) + " in URL: " + str(url)
                status = "error"
                current_try += 1
                print("Retrying " + str(url) + " because of HTTP code: " + str(resp.status_code))
            elif resp.status_code != 200: # any other kind of error
                message = "ERROR: HerediCare API endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text) + " in URL: " + str(url)
                status = "error"
                retry = False
            else: # request was successful
                resp = resp.json(strict=False)
                new_items = resp[items_key]
                result.extend(new_items)
                has_next = resp["hasMore"]
                if has_next:
                    found_next = False
                    for link in resp["links"]:
                        if link["rel"] == "next":
                            url = link["href"]
                            found_next = True
                    if not found_next:
                        message = "ERROR: response 'hasMore' attribute is true but no 'next' url found."
                        status = "error"
                        has_next = False # prevent infinite loop in case the next url is missing for some reason
                        retry = False
                else:
                    retry = False # for safety, has_next is false anyway
        return status, message, result

    def get_post_regexes(self):
        status = "success"
        message = ""
        all_items = []
        project_type = "upload"

        url = self.get_url(project_type, "post_info") # first url
        status, message, all_items = self.iterate_pagination(url, project_type)

        #with open("/mnt/storage2/users/ahdoebm1/HerediVar/src/common/heredicare_interface_debug/post_fields.json", "w") as f:
        #    functions.prettyprint_json(all_items, func = f.write)

        result = {}
        for item in all_items:
            item_name = item["item_name"]
            regex = item["item_regex_format"]
            result[item_name] = regex

        return result, status, message

    def get_new_submission_id(self):
        status = "success"
        message = ""
        submission_id = None
        project_type = "upload"

        url = self.get_url(project_type, "submissionid")
        status, message, all_items = self.iterate_pagination(url, project_type)

        if status == "success":
            submission_id = all_items[0]["submission_id"]
            
        return submission_id, status, message
    
    def get_new_record_id(self):
        status = "success"
        message = ""
        record_id = None
        project_type = "upload"

        url = self.get_url(project_type, "recordid")
        status, message, all_items = self.iterate_pagination(url, project_type)

        if status == "success": # success
            record_id = all_items[0]["record_id"]

        return record_id, status, message

    def get_submission_status(self, submission_id):
        status = "success"
        message = ""
        finished_at = None
        project_type = "upload"

        if submission_id is None:
            status = "pending"
            return finished_at, status, message

        url = self.get_url(project_type, "submission_status", [str(submission_id)])
        status, message, all_items = self.iterate_pagination(url, project_type)

        if status == "error":
            status = "retry"
        if status == "success": # success
            
            if len(all_items) == 0: # submission id was generated but no data was posted yet
                status = "pending"
            else:
                info = all_items[0]
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
        preferred_gene = None
        preferred_transcript = None
        if transaction_type == 'INSERT':
            preferred_gene = variant.get_genes(how = "best", within_gene = True)
            if preferred_gene is not None:
                consequences = variant.get_sorted_consequences()
                for consequence in consequences:
                    if consequence.transcript.gene is None:
                        continue
                    if consequence.transcript.gene.symbol == preferred_gene:
                        preferred_consequence = consequence
                        preferred_transcript = consequence.transcript.name
                        break

            if preferred_consequence is None:
                status = "skipped"
                message = "Intergenic variants are not supported for upload to HerediCaRe"
                return all_items, status, message

        preferred_transcript = preferred_consequence.transcript.name if preferred_consequence is not None else None
        preferred_gene = preferred_consequence.transcript.gene.symbol if preferred_consequence is not None else None

        #print(preferred_gene)
        #print(preferred_consequences)
        #print(preferred_consequence)
        #print(preferred_transcript)

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
        if not self.is_valid_post_data(new_value, item_regex, none_allowed = True):
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
            if not self.is_valid_post_data(new_value, item_regex, none_allowed = True):
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
            if not self.is_valid_post_data(new_value, item_regex, none_allowed = True):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return all_items, status, message
            old_value = None
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)

        return all_items, status, message



    def get_consensus_classification_items(self, variant, vid, submission_id, post_regexes, transaction_type):
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
        #elif mrcc.selected_class in ["R", "4M", "5M"]:
        #    status = "error"
        #    message = "Currently, R and 4M classifications cannot be uploaded to HerediCaRe."
        #    return all_items, status, message

        heredicare_variant, status, message = self.get_variant(vid)
        if status == 'error':
            return all_items, status, message
        
        # add consensus classification class in HerediCare format: PATH_TF
        item_name = "PATH_TF"
        item_regex = post_regexes[item_name]
        new_value = functions.num2heredicare(mrcc.selected_class, single_value=True)
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = heredicare_variant["PATH_TF"] if transaction_type == 'UPDATE' else None #self.get_heredicare_consensus_attribute(variant, vid, "selected_class")
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
        #old_consensus_classification_date = self.get_heredicare_consensus_attribute(variant, vid, "classification_date")
        #old_value = old_consensus_classification_date if old_consensus_classification_date is None else old_consensus_classification_date.strftime('%d.%m.%Y')
        old_value = heredicare_variant["VUSTF_DATUM"] if transaction_type == 'UPDATE' else None
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        # add comment of consensus classification: VUSTF_21
        item_name = "VUSTF_21"
        item_regex = post_regexes[item_name]
        new_value = mrcc.get_extended_comment()
        if not self.is_valid_post_data(new_value, item_regex):
            status = "error"
            message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
            return all_items, status, message
        old_value = heredicare_variant["VUSTF_21"] if transaction_type == 'UPDATE' else None #self.get_heredicare_consensus_attribute(variant, vid, "comment")
        new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
        all_items.append(new_item)

        return all_items, status, message


    def is_valid_post_data(self, value, regex, none_allowed = False):
        if value is None:
            if none_allowed:
                return True
            return False
        pattern = re.compile(regex)
        result = pattern.match(json.dumps(value)[1:-1])
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
            consensus_classification_items, status, message = self.get_consensus_classification_items(variant, vid, submission_id, post_regexes, transaction_type)
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
            all_items[i]["item_value_old"] = functions.none2default(all_items[i]["item_value_old"], "")
            all_items[i]["item_value_new"] = functions.none2default(all_items[i]["item_value_new"], "")
        
        # tinker all items together
        data = {'items': all_items}
        if os.environ.get('WEBAPP_ENV', '') == 'dev':
            with open('/mnt/storage2/users/ahdoebm1/HerediVar/src/common/heredicare_interface_debug/sub' + str(submission_id) + '.json', "w") as f:
                functions.prettyprint_json(data, f.write)
        data = json.dumps(data)

        return data, vid, submission_id, status, message


    def _post_data(self, data):
        status = "success"
        message = ""
        project_type = "upload"

        retry = True
        max_tries = 3
        backoff_mult = 20
        current_try = 0

        while retry and (current_try <= max_tries):
            status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
            if status == 'error':
                break
            
            url = self.get_url(project_type, "send_data")
            bearer, timestamp = self.get_saved_bearer(project_type)
            header = {"Authorization": "Bearer " + bearer}

            time.sleep(current_try * backoff_mult)
            resp = requests.post(url, headers=header, data=data)

            if resp.status_code in [401, 503]: # unauthorized, service unavailable --> retry these
                message = "ERROR: HerediCare API post variant data endpoint returned an HTTP "  + str(resp.status_code)
                status = "error"
                current_try += 1
            elif resp.status_code == 555:
                message = "ERROR: HerediCare API post variant data endpoint returned an HTTP 555 error. Reason: " + urllib.parse.unquote(resp.headers.get("Error-Reason", "not provided"))
                status = "error"
                retry = False
            elif resp.status_code != 200:
                message = "ERROR: HerediCare API post variant data endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
                status = "error"
                retry = False
            else: # success
                status = "success"
                message = ""
                retry = False

        return status, message

    def post(self, variant, vid, options):
        status = "success"
        message = ""

        data, vid, submission_id, status, message = self.get_data(variant, vid, options)
        if status in ["error", "skipped"]:
            return vid, submission_id, status, message
        
        #print(data)
        status, message = self._post_data(data)

        return vid, submission_id, status, message

