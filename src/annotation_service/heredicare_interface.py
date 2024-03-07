
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common.functions as functions
from common.xml_validator import xml_validator
from datetime import datetime, timedelta
from common.singleton import Singleton





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
    bearer = None
    bearer_timestamp = None

    def __init__(self):
        self.base_url = "https://hazel.imise.uni-leipzig.de"
        self.endpoints = {"bearer": "pids2/heredivar/oauth/token",
                          "vid_list": "pids2/heredivar/get/vars",
                          "variant": "pids2/heredivar/vars"}
        #self.bearer = None
        #self.bearer_timestamp = None

        print("NEW INSTANCE")


    def get_bearer(self):
        message = ""
        bearer = None
        status = "success"
        url = self.base_url + "/" + self.endpoints["bearer"]
        data = {"grant_type":"client_credentials"}
        auth = (os.environ.get("HEREDICARE_CLIENT_ID"), os.environ.get("HEREDICARE_CLIENT_PASSWORD"))
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


    def update_token(self, timestamp):
        new_bearer, status, message = self.get_bearer()
        if status == 'success':
            Heredicare.bearer = new_bearer
            Heredicare.bearer_timestamp = timestamp
            print("UPDATED TOKEN!!!!")
        return status, message

    def introspect_token(self):
        now = datetime.now()
        status = "success"
        message = ""
        #print("TOKEN: " + str(self.bearer))
        if Heredicare.bearer is None:
            status, message = self.update_token(now)
        elif Heredicare.bearer_timestamp + timedelta(minutes = 50) <= now:
            status, message = self.update_token(now)
        return status, message



    def get_vid_list(self):
        status = "success"
        message = ""
        vids = []

        status, message = self.introspect_token() # checks validity of the token and updates it if neccessary
        if status == 'error':
            return vids, status, message

        url = self.base_url + "/" + self.endpoints["vid_list"]
        header = {"Authorization": "Bearer " + Heredicare.bearer}

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
            current_vid = vid_raw['record_id']
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

        status, message = self.introspect_token() # checks validity of the token and updates it if neccessary
        if status == 'error':
            return variant, status, message

        url = self.base_url + "/" + self.endpoints["variant"] + "/" + str(vid)
        header = {"Authorization": "Bearer " + Heredicare.bearer}

        resp = requests.get(url, headers=header)
        if resp.status_code == 401: # unauthorized
            message = "ERROR: HerediCare API get vid list endpoint returned an HTTP 401, unauthorized error. Attempting retry."
            status = "retry"
        elif resp.status_code == 404: # deleted
            message = "WARNING: The HerediCare API returned status code 404 For vid " + str(vid)
            status = "deleted"
        elif resp.status_code != 200:
            message = "ERROR: HerediCare API get variant details endpoint returned an HTTP " + str(resp.status_code) + " error: " + self.extract_error_message(resp.text)
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