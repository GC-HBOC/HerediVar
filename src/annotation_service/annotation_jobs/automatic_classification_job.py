
from ._job import Job
import common.paths as paths
import common.functions as functions
from common.db_IO import Connection
import os
import json
import requests
import urllib
from os import path
import jsonschema


## this annotates various information from different vcf files
class automatic_classification_job(Job):
    def __init__(self, annotation_data):
        self.job_name = "automatic classification"
        self.status = "pending"
        self.err_msg = ""
        self.annotation_data = annotation_data
        self.generated_paths = []


    def do_execution(self, *args, **kwargs):
        result = True
        job_config = kwargs['job_config']
        if not any(job_config[x] for x in ["do_auto_class"]):
            result = False
            self.status = "skipped"
            return result

        # require all jobs to be successful or skipped
        queue = kwargs['queue']
        for job in queue: 
            if job.job_name != self.job_name:
                successful_job = self.require_job(job, queue)
                if not successful_job:
                    result = False
                    self.status = "skipped"
        return result
    

    def execute(self, conn):
        # update state
        self.status = "progress"
        self.print_executing()
    
        # get arguments
        variant_id = self.annotation_data.variant.id
    
        # execute and save to db
        self.save_to_db(variant_id, conn) # raises runtime error when autoclass service yields error
    
        # update state
        self.status = "success"



    def save_to_db(self, variant_id, conn: Connection):
        conn.clear_automatic_classification(variant_id)

        autoclass_input = self.get_autoclass_json(variant_id, conn)

        if autoclass_input is None:
            return 0, "Not enough information to calculate the automatic classification"

        returncode, err_msg, classification = self.run_automatic_classification(autoclass_input, paths.automatic_classification_config_path)

        if returncode != 0:
            raise RuntimeError(err_msg)

        classification_result = json.loads(classification["result"])
        scheme_alias = classification.get("scheme_name", "acmg_svi")
        scheme_version = classification["scheme_version"]
        classification_scheme_id = conn.get_classification_scheme_id_from_alias(scheme_alias, scheme_version)
        if classification_scheme_id is None:
            raise ValueError("The scheme provided by the config: " + str(scheme_alias) + " version " + scheme_version + " is not in HerediVar. Please adjust config, insert scheme or add scheme alias.")
        scheme = conn.get_classification_scheme(classification_scheme_id)
        scheme_id = scheme[0]
        scheme_type = scheme[3]
        scheme_version = scheme[7]
        tool_version = classification["tool_version"]

        selected_criteria = {} # protein, splicing, general
        for criterium_name in classification_result:
            current_criterium = classification_result[criterium_name]
            if not current_criterium['status']:
                continue

            rule_type = current_criterium['rule_type']
            criterium_name_cut = criterium_name.strip().split('_')[0].lower()

            prefix = self.evidence_type2prefix(current_criterium['evidence_type'])
            postfix = self.strength2postfix(current_criterium['strength'])
            criterium_strength_abbr = prefix + postfix

            criterium_complex = criterium_name_cut + '_' + criterium_strength_abbr
            if criterium_complex == 'bp1_bs' and ('brca' in scheme_type.lower() and scheme_version == "v1.1.0"):
                functions.extend_dict(selected_criteria, rule_type, criterium_complex)
            elif criterium_complex == 'pvs1_pp' and ('atm' in scheme_type.lower() and scheme_version == "v1.3.0"):
                functions.extend_dict(selected_criteria, rule_type, criterium_complex) 
            elif criterium_complex == 'pm2_pp' and ('atm' in scheme_type.lower() and scheme_version in ["v1.1.0", "v1.3.0"]):
                functions.extend_dict(selected_criteria, rule_type, criterium_complex)
            else:
                functions.extend_dict(selected_criteria, rule_type, criterium_strength_abbr)
        
        # calculate class for splicing
        selected_criteria_splicing = '+'.join(selected_criteria.get("splicing", []) + selected_criteria.get("general", []))
        classification_splicing = self.get_classification(selected_criteria_splicing, scheme_type, scheme_version)
        point_classification_splicing, point_score_splicing = self.get_points(selected_criteria_splicing, scheme_type, scheme_version)
        
        # calculate class for protein
        selected_criteria_protein = '+'.join(selected_criteria.get("protein", []) + selected_criteria.get("general", []))
        classification_protein = self.get_classification(selected_criteria_protein, scheme_type, scheme_version)
        point_classification_protein, point_score_protein = self.get_points(selected_criteria_protein, scheme_type, scheme_version)

        automatic_classification_id = conn.insert_automatic_classification(
            variant_id, 
            scheme_id, 
            classification_splicing, 
            classification_protein, 
            point_classification_splicing, 
            point_score_splicing, 
            point_classification_protein,
            point_score_protein, 
            tool_version
        )

        for criterium_name in classification_result:
            current_criterium = classification_result[criterium_name]
            conn.insert_automatic_classification_criterium_applied(
                automatic_classification_id = automatic_classification_id,
                name = criterium_name.split('_')[0],
                rule_type = current_criterium["rule_type"],
                evidence_type = current_criterium["evidence_type"],
                strength = current_criterium["strength"],
                type = self.evidence_type2prefix(current_criterium['evidence_type']) + self.strength2postfix(current_criterium['strength']),
                comment = current_criterium["comment"],
                state = "selected" if current_criterium["status"] else "unselected"
            )
        
    
    def get_classification(self, selected_criteria: str, scheme: str, version: str):
        host = os.environ.get("HOST", "localhost") + ":" + os.environ.get("PORT", "5000")
        classification_endpoint = urllib.parse.urljoin("http://" + host, "calculate_class/" + scheme + "/" + version + "/" + selected_criteria)
        resp = requests.get(classification_endpoint)
        resp.raise_for_status()
        result = resp.json()
        if "final_class" not in result:
            raise RuntimeError("The classification endpoint did not return a classification")
        classification = result.get("final_class")

        return classification
    
    def get_points(self, selected_criteria: str, scheme: str, version: str):
        host = os.environ.get("HOST", "localhost") + ":" + os.environ.get("PORT", "5000")
        classification_endpoint = urllib.parse.urljoin("http://" + host, "calculate_point_score/" + scheme + "/" + version + "/" + selected_criteria)
        resp = requests.get(classification_endpoint)
        resp.raise_for_status()
        result = resp.json()
        if "points" not in result or "classification" not in result:
            raise RuntimeError("The point score endpoint did not return a classification")
        point_class = result["classification"]
        point_score = result["points"]
        return point_class, point_score

    def evidence_type2prefix(self, evidence_type):
        mapping = {"benign": "b", "pathogenic": "p"}
        return mapping[evidence_type]
    
    def strength2postfix(self, strength):
        mapping = {"very_strong": "vs", "strong": "s", "moderate": "m", "supporting": "p", "stand_alone": "a"}
        return mapping[strength]


    def run_automatic_classification(self, autoclass_input: str, config_path: str):
        ## THE CLI
        #automatic_classification_python = os.path.join(paths.automatic_classification_path, ".venv/bin/python3")
        #command = [automatic_classification_python, os.path.join(paths.automatic_classification_path, "variant_classification/classify.py")]
        #command.extend([ "-c", config_path, "-i", autoclass_input])
        #returncode, stderr, stdout = functions.execute_command(command, 'Automatic_Classification')
        
        ## THE API
        #curl -X 'POST' \
        #    'http://0.0.0.0:8080/classify_variant' \
        #    -H 'accept: application/json' \
        #    -H 'Content-Type: application/json' \
        #    -d '{
        #    "config_path": "/home/katzkean/variant_classification/config.yaml",
        #    "variant_json": "{\"chr\": \"17\", \"pos\": 43057110, \"gene\": \"BRCA1\", \"ref\": \"A\", \"alt\": \"C\", \"variant_type\": [\"missense_variant\"], \"variant_effect\": [{\"transcript\": \"ENST00000357654\", \"hgvs_c\": \"c.5219T>G\", \"hgvs_p\": \"p.Val1740Gly\", \"variant_type\": [\"missense_variant\"], \"exon\": 19}, {\"transcript\": \"ENST00000471181\", \"hgvs_c\": \"c.5282T>G\", \"hgvs_p\": \"p.Val1761Gly\", \"variant_type\": [\"missense_variant\"], \"exon\": 20}], \"splicing_prediction_tools\": {\"SpliceAI\": 0.5}, \"pathogenicity_prediction_tools\": {\"REVEL\": 0.5, \"BayesDel\": 0.5}, \"gnomAD\": {\"AF\": 0.007, \"AC\": 12, \"popmax\": \"EAS\", \"popmax_AF\": 0.009, \"popmax_AC\": 5}, \"FLOSSIES\": {\"AFR\": 9, \"EUR\": 130}, \"mRNA_analysis\": {\"performed\": true, \"pathogenic\": true, \"benign\": true}, \"functional_data\": {\"performed\": true, \"pathogenic\": true, \"benign\": true}, \"prior\": 0.25, \"co-occurrence\": 0.56, \"segregation\": 0.56, \"multifactorial_log-likelihood\": 0.56, \"VUS_task_force_domain\": true, \"cancer_hotspot\": true, \"cold_spot\": true}"
        #}'
        api_host = "http://" + os.environ.get("AUTOCLASS_HOST", "0.0.0.0") + ":" + os.environ.get("AUTOCLASS_PORT", "8080") + "/"
        endpoint = "classify_variant"
        url = api_host + endpoint
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"config_path": config_path, "variant_json": autoclass_input}
        data = json.dumps(data)
        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code != 200:
            status_code = resp.status_code
            stderr = resp.text
            stdout = ""
        else:
            status_code = 0
            stderr = ""
            stdout = resp.json()

        return status_code, stderr, stdout

    def get_autoclass_json(self, variant_id, conn: Connection) -> str:
        variant = conn.get_variant(variant_id, include_clinvar=False, include_consensus=False, include_user_classifications=False, include_heredicare_classifications=False, include_literature = False, include_external_ids = False, include_automatic_classification=False)
        
        if variant is None:
            return None
        if len(variant.ref) > 15 or len(variant.alt) > 15: # cannot calculate on long insertions/deletions
            return None
        
        result = {}

        # basic info
        result["chr"] = variant.chrom
        result["pos"] = variant.pos
        result["ref"] = variant.ref
        result["alt"] = variant.alt

        # gene & consequence summary
        best_gene = variant.get_genes(how = "best", within_gene = True)
        if best_gene is None:
            return None
        
        result["gene"] = best_gene
        all_variant_types = []
        if variant.consequences is not None:
            for consequence in variant.consequences:
                if consequence.transcript.gene.symbol is None:
                    continue
                if consequence.transcript.source == "ensembl" and best_gene.upper() == consequence.transcript.gene.symbol.upper():
                    new_variant_types = consequence.consequence.split('&')
                    new_variant_types = [x.strip().replace(' ', '_') for x in new_variant_types]
                    all_variant_types.extend(new_variant_types)
        if len(all_variant_types) == 0:
            return None
        result["variant_type"] = list(set(all_variant_types))


        # all consequences
        variant_effects = []
        if variant.consequences is not None:
            for consequence in variant.consequences:
                if consequence.transcript.source == "ensembl" and consequence.hgvs_c is not None and consequence.hgvs_c.startswith('c') and consequence.transcript.gene.symbol is not None:
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
            all_scores = []
            for spliceai_score in spliceai_scores.value.split(','):
                if spliceai_score != '.':
                    all_scores.append(float(spliceai_score))
            if len(all_scores) > 0:
                splicing_prediction_scores["SpliceAI"] = max(all_scores)
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
        if all([x is not None for x in [variant.annotations.gnomad_af, variant.annotations.gnomad_ac]]):
            gnomad_scores["AF"] = variant.annotations.gnomad_af.get_value()
            gnomad_scores["AC"] = variant.annotations.gnomad_ac.get_value()
            if all([x is not None for x in [variant.annotations.gnomad_popmax, variant.annotations.gnomad_popmax_AC, variant.annotations.gnomad_popmax_AF, variant.annotations.faf95_popmax]]):
                gnomad_scores["subpopulation"] = variant.annotations.gnomad_popmax.get_value()
                gnomad_scores["popmax_AC"] = variant.annotations.gnomad_popmax_AC.get_value()
                gnomad_scores["popmax_AF"] = variant.annotations.gnomad_popmax_AF.get_value()
                gnomad_scores["faf_popmax_AF"] = variant.annotations.faf95_popmax.get_value()
            else: # if the variant is missing popmax values simply use the standard af and ac
                gnomad_scores["subpopulation"] = "ALL"
                gnomad_scores["popmax_AC"] = variant.annotations.gnomad_ac.get_value()
                gnomad_scores["popmax_AF"] = variant.annotations.gnomad_af.get_value()
                gnomad_scores["faf_popmax_AF"] = variant.annotations.gnomad_af.get_value()
            
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
        "mRNA_analysis" : [
        {"minigene": true,
         "patient_rna": false,
         "allelic" : "Construct",
         "quantification": null}
        ],
        """
        assays_dict = variant.order_assays_by_type()

        splicing_assays = assays_dict.get("splicing")

        #print(splicing_assays)

        all_splicing_assays = []
        if splicing_assays is not None:
            for assay in splicing_assays:
                if assay.metadata.get("minigene") is None or assay.metadata.get("patient_rna") is None or assay.metadata.get("allele_specific") is None: # skip legacy assays
                    continue
                minigene = assay.get_metadata_value("minigene", "False") == "True"
                patient_rna = assay.get_metadata_value("patient_rna", "False") == "True"
                allelic = assay.get_metadata_value("allele_specific", "False")
                quantification = functions.percent_to_decimal(assay.get_metadata_value("minimal_percentage", None))
                all_splicing_assays.append({"minigene": minigene,
                                            "patient_rna": patient_rna,
                                            "allelic": allelic,
                                            "quantification": quantification})
        
        result["mRNA_analysis"] = all_splicing_assays


        # functional data:
        """
        "functional_data": [
        {"pathogenic": false,
         "benign": true},
        {"pathogenic": false,
         "benign": true}
        ]
        """
        functional_assays = assays_dict.get("functional")

        all_functional_assays = []
        if functional_assays is not None:
            for assay in functional_assays:
                if assay.metadata.get("functional_category") is None or assay.metadata.get("functional_category") is None: # skip legacy assays
                    continue
                is_pathogenic = assay.get_metadata_value("functional_category", "") == "pathogenic"
                is_benign = assay.get_metadata_value("functional_category", "") == "benign"
                all_functional_assays.append({"pathogenic": is_pathogenic,
                                              "benign": is_benign})
        result["functional_data"] = all_functional_assays
        

        # heredicare computed scores: currently missing
        """
        "prior": 0.25,
        "co-occurrence" : 0.56,
        "segregation" : 0.56,
        "multifactorial_log-likelihood": 0.56,
        """

        # protein domains:
        """
        "VUS_task_force_domain" : true,
        "cold_spot": true
        """
        can_have_task_force_protein_domain = False
        all_genes = variant.get_genes(how = "list")
        for gene_symbol in all_genes:
            can_have_task_force_protein_domain = conn.has_task_force_protein_domains(gene_symbol)
            if can_have_task_force_protein_domain:
                break
        if can_have_task_force_protein_domain:
            result["VUS_task_force_domain"] = False
            if variant.annotations.task_force_protein_domain is not None:
                result["VUS_task_force_domain"] = True
        
        result["cold_spot"] = False
        if variant.annotations.coldspot is not None:
            result["cold_spot"] = True

        # cancerhotspots
        """
        "cancer_hotspot": true,
        """
        cancerhotspots_ac = variant.annotations.cancerhotspots_ac
        cancerhotspots_af = variant.annotations.cancerhotspots_af
        cancerhotspots = {}
        if cancerhotspots_af is not None:
            cancerhotspots["AF"] = cancerhotspots_af.get_value()
        if cancerhotspots_ac is not None:
            cancerhotspots["AC"] = cancerhotspots_ac.get_value()
        result["cancer_hotspots"] = cancerhotspots

        validate_input(result) # raises an error on fails

        result_json = json.dumps(result)

        #print(result_json)

        return result_json


def validate_input(input: dict):
    json_schema_path = path.join(paths.automatic_classification_path, "API/schema_input.json")
    with open(json_schema_path) as f:
        json_schema = json.load(f)
    jsonschema.validate(input, json_schema) # this raises an error if it fails



