
from ._job import Job
import common.paths as paths
import common.functions as functions
from common.db_IO import Connection
import tempfile
import os
import json
import requests
import urllib


## this annotates various information from different vcf files
class automatic_classification_job(Job):
    def __init__(self, job_config):
        self.job_name = "vcf annotate from vcf"
        self.job_config = job_config


    def execute(self, inpath, annotated_inpath, **kwargs):
        if not any(self.job_config[x] for x in ['do_auto_class']):
            return 0, '', ''

        self.print_executing()

        return 0, "", ""



    def save_to_db(self, info, variant_id, conn: Connection):
        err_msg = ""
        status_code = 0

        if not any(self.job_config[x] for x in ['do_auto_class']):
            return status_code, err_msg

        autoclass_input = self.get_autoclass_json(variant_id, conn)
        #print(autoclass_input)
        config_path = os.path.join(paths.automatic_classification_path, "config_production.yaml")
        returncode, err_msg, classification_result = self.run_automatic_classification(autoclass_input, config_path)

        if returncode != 0:
            raise RuntimeError(err_msg)

        print(classification_result)

        classification_result = json.loads(classification_result)

        conn.clear_automatic_classification(variant_id)
        
        scheme = "acmg-svi"
        selected_criteria = []
        for criterium_name in classification_result:
            current_criterium = classification_result[criterium_name]
            if not current_criterium['status']:
                continue
            prefix = self.evidence_type2prefix(current_criterium['evidence_type'])
            postfix = self.strength2postfix(current_criterium['strength'])
            selected_criteria.append(prefix+postfix)
        selected_criteria = '+'.join(selected_criteria)

        classification_endpoint = os.environ.get("HOST", "localhost") + ":" + os.environ.get("PORT", "5000")
        classification_endpoint = urllib.parse.urljoin("http://" + classification_endpoint, "calculate_class/" + scheme + "/" + selected_criteria)
        resp = requests.get(classification_endpoint)
        resp.raise_for_status()
        classification = resp.json().get("final_class")
        if classification is None:
            raise RuntimeError("The classification endpoint did not return a classification")
        automatic_classification_id = conn.insert_automatic_classification(variant_id, scheme, classification)

        for criterium_name in classification_result:
            current_criterium = classification_result[criterium_name]
            conn.insert_automatic_classification_criterium_applied(
                automatic_classification_id = automatic_classification_id,
                name = criterium_name,
                rule_type = current_criterium["rule_type"],
                evidence_type = current_criterium["evidence_type"],
                strength = current_criterium["strength"],
                comment = current_criterium["comment"],
                is_selected = 1 if current_criterium["status"] else 0
            )

        return status_code, err_msg

    def evidence_type2prefix(self, evidence_type):
        mapping = {"benign": "p", "pathogenic": "p"}
        return mapping[evidence_type]
    
    def strength2postfix(self, strength):
        mapping = {"very_strong": "vs", "strong": "s", "moderate": "m", "supporting": "p", "stand_alone": "a"}
        return mapping[strength]


    def run_automatic_classification(self, autoclass_input, config_path):
        automatic_classification_python = os.path.join(paths.automatic_classification_path, ".venv/bin/python3")
        command = [automatic_classification_python, os.path.join(paths.automatic_classification_path, "variant_classification/classify.py")]
        command.extend([ "-c", config_path, "-i", autoclass_input])

        returncode, stderr, stdout = functions.execute_command(command, 'Automatic_Classification')

        return returncode, stderr, stdout

    def get_autoclass_json(self, variant_id, conn: Connection) -> str:
        with open("/mnt/storage2/users/ahdoebm1/HerediVar/src/tools/variant_classification/API/example_input.json", "r") as intest:
            result = intest.read()
        return result
