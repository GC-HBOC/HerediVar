
from ._job import Job
import common.paths as paths
import common.functions as functions
from common.db_IO import Connection
import tempfile
import os
import json
import requests
import urllib
from os import path
import jsonschema


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

        #print(classification_result)

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
        #print(classification_endpoint)
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
                type = self.evidence_type2prefix(current_criterium['evidence_type']) + self.strength2postfix(current_criterium['strength']),
                comment = current_criterium["comment"],
                is_selected = 1 if current_criterium["status"] else 0
            )

        return status_code, err_msg

    def evidence_type2prefix(self, evidence_type):
        mapping = {"benign": "b", "pathogenic": "p"}
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
        variant = conn.get_variant(variant_id, include_clinvar=False, include_consensus=False, include_user_classifications=False, include_heredicare_classifications=False, include_literature = False, include_external_ids = False, include_automatic_classification=False)
        result = {}

        # basic info
        result["chr"] = variant.chrom
        result["pos"] = variant.pos
        result["ref"] = variant.ref
        result["alt"] = variant.alt

        # gene & consequence summary
        all_genes = variant.get_genes(how = "list")
        result["gene"] = all_genes[0]
        all_variant_types = []
        for consequence in variant.consequences:
            if consequence.transcript.source == "ensembl":
                new_variant_types = consequence.consequence.split('&')
                new_variant_types = [x.strip().replace(' ', '_') for x in new_variant_types]
                all_variant_types.extend(new_variant_types)
        result["variant_type"] = list(set(all_variant_types))

        # all consequences
        variant_effects = []
        for consequence in variant.consequences:
            if consequence.transcript.source == "ensembl" and consequence.hgvs_c is not None:
                new_effect = {}
                new_effect["transcript"] = consequence.transcript.name
                new_effect["variant_type"] = [x.strip().replace(' ', '_') for x in consequence.consequence.split('&')]
                if consequence.hgvs_c is not None: # this is a required field, throw error if it is missing!
                    new_effect["hgvs_c"] = consequence.hgvs_c
                if consequence.hgvs_p is not None:
                    new_effect["hgvs_p"] = consequence.hgvs_p
                if consequence.exon is not None:
                    new_effect["exon"] = int(consequence.exon)
                if consequence.intron is not None:
                    new_effect["intron"] = int(consequence.intron)
                variant_effects.append(new_effect)
        result["variant_effect"] = variant_effects

        # splicing prediction
        splicing_prediction_scores = {}
        spliceai_scores = variant.annotations.spliceai_max_delta
        if spliceai_scores is not None:
            spliceai_score = max([float(x) for x in spliceai_scores.value.split(',')])
            splicing_prediction_scores["SpliceAI"] = spliceai_score
        if len(splicing_prediction_scores) > 0: # only insert if at least one splicing score available
            result["splicing_prediction_tools"] = splicing_prediction_scores

        # pathogenicity prediction
        pathogenicity_scores = {}
        if variant.annotations.revel is not None:
            revel_max_transcript, revel_max_val = variant.annotations.revel.max()
            pathogenicity_scores["REVEL"] = revel_max_val
        if variant.annotations.bayesdel is not None:
            pathogenicity_scores["BayesDel"] = variant.annotations.bayesdel.get_value()
        if len(pathogenicity_scores) > 0: # only insert if at least one pathogenicity score available
            result["pathogenicity_prediction_tools"] = pathogenicity_scores

        # gnomAD scores
        gnomad_scores = {}
        if variant.annotations.gnomad_af is not None:
            gnomad_scores["AF"] = variant.annotations.gnomad_af.get_value()
        if variant.annotations.gnomad_ac is not None:
            gnomad_scores["AC"] = variant.annotations.gnomad_ac.get_value()
        if variant.annotations.gnomad_popmax is not None:
            gnomad_scores["popmax"] = variant.annotations.gnomad_popmax.get_value()
        if variant.annotations.gnomad_popmax_AC is not None:
            gnomad_scores["popmax_AC"] = variant.annotations.gnomad_popmax_AC.get_value()
        if variant.annotations.gnomad_popmax_AF is not None:
            gnomad_scores["popmax_AF"] = variant.annotations.gnomad_popmax_AF.get_value()
        if len(gnomad_scores) > 0:
            result["gnomAD"] = gnomad_scores

        # FLOSSIES scores
        """
        "FLOSSIES":
        {"AFR" : 9,
         "EUR" : 130},
        """
        flossies_scores = {}
        if variant.annotations.flossies_num_afr is not None:
            flossies_scores["AFR"] = variant.annotations.flossies_num_afr.get_value()
        if variant.annotations.flossies_num_eur is not None:
            flossies_scores["EUR"] = variant.annotations.flossies_num_eur.get_value()
        if len(flossies_scores) > 0:
            result["FLOSSIES"] = flossies_scores

        # mRNA analyses: currently missing
        """
        "mRNA_analysis" :
        {"performed": true,
         "pathogenic": true,
         "benign": true},
        """
        result["mRNA_analysis"] = {"performed": False,
                                   "pathogenic": False,
                                   "benign": False}

        # functional data: currently missing
        """
        "functional_data":
        {"performed": true,
         "pathogenic": true,
         "benign": true},
        """
        result["functional_data"] = {"performed": False,
                                     "pathogenic": False,
                                     "benign": False}

        # heredicare computed scores: currently missing
        """
        "prior": 0.25,
        "co-occurrence" : 0.56,
        "segregation" : 0.56,
        "multifactorial_log-likelihood": 0.56,
        """

        # protein domains: cold_spot missing
        """
        "VUS_task_force_domain" : true,
        "cold_spot": true
        """
        can_have_task_force_protein_domain = False
        for gene_symbol in all_genes:
            can_have_task_force_protein_domain = conn.has_task_force_protein_domains(gene_symbol)
            if can_have_task_force_protein_domain:
                break
        if can_have_task_force_protein_domain:
            result["VUS_task_force_domain"] = False
            if variant.annotations.task_force_protein_domain is not None:
                result["VUS_task_force_domain"] = True
        
        #result["cold_spot"] = False
        #if variant.annotations.task_force_cold_spot is not None:
        #    result["cold_spot"] = True

        # cancerhotspots
        """
        "cancer_hotspot": true,
        """
        result["cancer_hotspot"] = False
        if variant.annotations.cancerhotspots_cancertypes is not None:
            result["cancer_hotspot"] = True

        validate_input(result) # raises an error on fails

        result_json = json.dumps(result)

        print(result_json)

        return result_json


def validate_input(input: dict):
    json_schema_path = path.join(paths.automatic_classification_path, "API/schema_input.json")
    with open(json_schema_path) as f:
        json_schema = json.load(f)
    jsonschema.validate(input, json_schema) # this raises an error if it fails