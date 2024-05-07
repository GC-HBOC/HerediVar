
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
            "submission_status": "vars/send/result"
        }
        #print("NEW INSTANCE")

    # path arguments must be in the correct order
    def get_url(self, project_type, endpoint, path_args = []): 
        url = self.base_url + "/" + self.projects[project_type] + "/" + self.endpoints[endpoint]
        if len(path_args) > 0:
            url += "/" + "/".join(path_args)
        print(url)
        return url

    def get_auth(self, project_type):
        if project_type == "download":
            auth = (os.environ.get("HEREDICARE_DOWNLOAD_CLIENT_ID"), os.environ.get("HEREDICARE_DOWNLOAD_CLIENT_PASSWORD"))
        elif project_type == "upload":
            auth = (os.environ.get("HEREDICARE_UPLOAD_CLIENT_ID"), os.environ.get("HEREDICARE_UPLOAD_CLIENT_PASSWORD"))
        return auth

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
            Heredicare.bearer[project_type] = new_bearer
            Heredicare.bearer_timestamp[project_type] = timestamp
            print("UPDATED TOKEN!!!!")
        return status, message

    def introspect_token(self, project_type):
        now = datetime.now()
        status = "success"
        message = ""
        #print("TOKEN: " + str(self.bearer))
        if Heredicare.bearer.get(project_type) is None:
            status, message = self.update_token(now, project_type)
        elif Heredicare.bearer_timestamp.get(project_type, now) + timedelta(minutes = 50) <= now:
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
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}

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
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}

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
            header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}
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
            if item_name == "PATH_TF":
                regex = r"^(-1|[1-4]|1[1-5]|2[01]|32|34)$"
            elif item_name == "VUSTF_DATUM":
                regex = r"^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[012])\.20\d\d$"
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
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}

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

    def get_postable_consensus_classification(self, variant, submission_id, post_regexes):
        status = "success"
        message = ""
        result = None
        consensus_classification = variant.get_recent_consensus_classification()

        # some sanity checks - maybe not neccessary, but its not bad to check those beforehand
        if consensus_classification is None or consensus_classification.selected_class is None or consensus_classification.selected_class == "-":
            return result, "error", "The variant does not have a consensus classification which can be submitted"
        
        vid_annotations = variant.get_external_ids("heredicare_vid") # post data to all valid vids

        all_items = []

        for annot in vid_annotations:
            vid = annot.value
            # add consensus classification class in HerediCare format: PATH_TF
            item_name = "PATH_TF"
            item_regex = post_regexes[item_name]
            new_value = functions.num2heredicare(consensus_classification.selected_class, single_value=True)
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return result, status, message
            old_value = self.get_heredicare_consensus_attribute(variant, vid, "selected_class")
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)

            # add date of consensus classification: VUSTF_DATUM
            item_name = "VUSTF_DATUM"
            item_regex = post_regexes[item_name]
            new_value = functions.reformat_date(consensus_classification.date, '%Y-%m-%d %H:%M:%S', '%d.%m.%Y')
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return result, status, message
            old_value = self.get_heredicare_consensus_attribute(variant, vid, "classification_date")
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)

            # add comment of consensus classification: VUSTF_15
            item_name = "VUSTF_15"
            item_regex = post_regexes[item_name]
            new_value = consensus_classification.get_extended_comment()
            if not self.is_valid_post_data(new_value, item_regex):
                status = "error"
                message = "The " + item_name + " (" + str(new_value) + ") from vid " + str(vid) + " does not match the expected regex pattern: " + item_regex
                return result, status, message
            old_value = self.get_heredicare_consensus_attribute(variant, vid, "comment")
            new_item = self.get_postable_item(record_id = vid, submission_id = submission_id, item_name = item_name, old_value = old_value, new_value = new_value)
            all_items.append(new_item)


        result = {"items": all_items}
        result = json.dumps(result)

        return result, status, message

    def terminate_transaction(self, submission_id, transaction_type):
        status = "success"
        message = ""
        project_type = "upload"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return status, message

        url = self.get_url(project_type, "send_data")
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}
        all_items = []
        # add terminating item to transaction
        all_items.append(self.get_terminating_item(submission_id, transaction_type))
        data = {"items": all_items}
        data = json.dumps(data)

        print("POST URL:" + url)
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

        #base_heredicare_debug_path = "/mnt/storage2/users/ahdoebm1/HerediVar/src/common/heredicare_interface_debug"
        #with open(os.path.join(base_heredicare_debug_path, "sub_" + str(submission_id) + ".txt"), "w") as f:
        #    f.write("DATA:\n")
        #    functions.prettyprint_json(json.loads(data), f.write)
        #    f.write("\n")
        #    f.write("RESPONSE MESSAGE:\n")
        #    f.write(message)

        return status, message


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

    def get_terminating_item(self, submission_id, update_insert):
        return {
            "submission_id": submission_id,
            "item_name": "RECORD_COMPLETE",
            "item_value_new": update_insert
        }

    def upload_consensus_classification(self, variant):
        status = "success"
        message = ""
        project_type = "upload"
        
        post_regexes, status, message = self.get_post_regexes()
        if status == "error":
            return status, message
        submission_id, status, message = self.get_new_submission_id()
        if status == 'error':
            return status, message

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return status, message

        url = self.get_url(project_type, "send_data")
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}
        data, status, message = self.get_postable_consensus_classification(variant, submission_id, post_regexes)

        if status == "error":
            return status, message

        print("POST URL:" + url)
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

        #base_heredicare_debug_path = "/mnt/storage2/users/ahdoebm1/HerediVar/src/common/heredicare_interface_debug"
        #with open(os.path.join(base_heredicare_debug_path, "sub_" + str(submission_id) + ".txt"), "w") as f:
        #    f.write("DATA:\n")
        #    functions.prettyprint_json(json.loads(data), f.write)
        #    f.write("\n")
        #    f.write("RESPONSE MESSAGE:\n")
        #    f.write(message)

        return submission_id, status, message


    def get_submission_status(self, submission_id):
        status = "success"
        message = ""
        result = None
        project_type = "upload"

        status, message = self.introspect_token(project_type) # checks validity of the token and updates it if neccessary
        if status == 'error':
            return result, status, message

        url = self.get_url(project_type, "submission_status", [str(submission_id)])
        header = {"Authorization": "Bearer " + Heredicare.bearer[project_type]}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get submission id endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API getsubmission id endpoint endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
            status = "error"
        else: # success
            result = resp.text
            
        return result, status, message


if __name__ == "__main__":
    functions.read_dotenv()
    heredicare_interface = Heredicare()

    variant_id_oi = "55"

    from common.db_IO import Connection
    conn = Connection(roles = ["db_admin"])
    variant = conn.get_variant(variant_id_oi)
    conn.close()

    submission_id, status, message = heredicare_interface.upload_consensus_classification(variant)
    print(submission_id)
    print(status)
    print(message)

    status, message = heredicare_interface.terminate_transaction(submission_id, "UPDATE")
    print(status)
    print(message)

    result, status, message = heredicare_interface.get_submission_status(submission_id)
    print(result)
    print(status)
    print(message)


    # 106
    result, status, message = heredicare_interface.get_submission_status(106)
    print(result)
    print(status)
    print(message)

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