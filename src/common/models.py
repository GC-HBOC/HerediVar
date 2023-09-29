from dataclasses import dataclass, asdict, fields
import json
from typing import Any
import common.functions as functions
from functools import cmp_to_key

@dataclass
class Annotation:
    id: int
    value: Any
    
    title: str
    display_title: str
    description: str
    version: str
    version_date: str
    value_type: str

    draw: bool = True

    def get_value(self):
        if self.value_type == 'text':
            return str(self.value)
        if self.value_type == 'int':
            return int(self.value)
        if self.value_type == 'float':
            return float(self.value)
        return self.value

    def to_vcf(self):
        data = self.title + '~1Y' + self.value
        return data
    
    def get_header(self):
        header = '##INFO=<ID=' + self.title + ',Number=1,Type=String,Description="' + self.description + ' (version: ' + str(self.version) +  ', version date: ' + str(self.version_date) + ' )">\n'
        return header



@dataclass
class AllAnnotations:
    rsid: Annotation = None

    phylop_100way: Annotation = None
    cadd_scaled: Annotation = None
    revel: Annotation = None
    
    spliceai_details: Annotation = None
    spliceai_max_delta: Annotation = None
    maxentscan_ref: Annotation = None
    maxentscan_alt: Annotation = None

    gnomad_ac: Annotation = None
    gnomad_af: Annotation = None
    gnomad_hom: Annotation = None
    gnomad_hemi: Annotation = None
    gnomad_het: Annotation = None
    gnomad_popmax: Annotation = None
    gnomadm_ac_hom: Annotation = None
    gnomad_popmax_AF: Annotation = None

    brca_exchange_clinical_significance: Annotation = None
    arup_classification: Annotation = None
    
    flossies_num_afr: Annotation = None
    flossies_num_eur: Annotation = None
    
    cancerhotspots_cancertypes: Annotation = None
    cancerhotspots_ac: Annotation = None
    cancerhotspots_af: Annotation = None

    tp53db_class: Annotation = None
    tp53db_DNE_LOF_class: Annotation = None
    tp53db_bayes_del: Annotation = None
    tp53db_DNE_class: Annotation = None
    tp53db_domain_function: Annotation = None
    tp53db_transactivation_class: Annotation = None

    heredicare_cases_count: Annotation = None
    heredicare_family_count: Annotation = None

    task_force_protein_domain: Annotation = None
    task_force_protein_domain_source: Annotation = None

    hexplorer: Annotation = None
    hexplorer_mut: Annotation = None
    hexplorer_wt: Annotation = None
    hexplorer_rev: Annotation = None
    hexplorer_rev_mut: Annotation = None
    hexplorer_rev_wt: Annotation = None
    max_hbond: Annotation = None
    max_hbond_mut: Annotation = None
    max_hbond_wt: Annotation = None
    max_hbond_rev: Annotation = None
    max_hbond_rev_mut: Annotation = None
    max_hbond_rev_wt: Annotation = None

    hci_prior: Annotation = None

    def get_all_annotation_names(self):
        return self.__annotations__

    def to_vcf(self):
        headers = {}
        info = []
        for annot in self.get_non_none_annotations():
            data = annot.to_vcf()
            header = annot.get_header()
            headers[annot.title] = header
            info.append(data)
        return headers, info

    def get_non_none_annotations(self):
        return [getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None]

    def flag_linked_annotations(self):
        self.setattr_advanced(self.spliceai_details, 'draw', False)
        self.setattr_advanced(self.spliceai_max_delta, 'draw', False)
        self.setattr_advanced(self.cancerhotspots_cancertypes, 'draw', False)
        self.setattr_advanced(self.hexplorer, 'draw', False)
        self.setattr_advanced(self.hexplorer_mut, 'draw', False)
        self.setattr_advanced(self.hexplorer_wt, 'draw', False)
        self.setattr_advanced(self.hexplorer_rev, 'draw', False)
        self.setattr_advanced(self.hexplorer_rev_mut, 'draw', False)
        self.setattr_advanced(self.hexplorer_rev_wt, 'draw', False)
        self.setattr_advanced(self.max_hbond, 'draw', False)
        self.setattr_advanced(self.max_hbond_mut, 'draw', False)
        self.setattr_advanced(self.max_hbond_wt, 'draw', False)
        self.setattr_advanced(self.max_hbond_rev, 'draw', False)
        self.setattr_advanced(self.max_hbond_rev_mut, 'draw', False)
        self.setattr_advanced(self.max_hbond_rev_wt, 'draw', False)
        self.setattr_advanced(self.arup_classification, 'draw', False)
        self.setattr_advanced(self.brca_exchange_clinical_significance, 'draw', False)
    
    def setattr_advanced(self, obj, var, val):
        if obj:
            setattr(obj, var, val)


    def get_group_identifiers(self):
        return ['Pathogenicity', 'Splicing', 'gnomAD', 'FLOSSIES', 'Cancerhotspots', 'TP53database', 'HerediCare', 'Protein Domain']

    def get_group(self, group_identifier):
        if group_identifier not in self.get_group_identifiers():
            return None
        if group_identifier == 'Protein Domain':
            return self.prepare_group([self.task_force_protein_domain, self.task_force_protein_domain_source])
        if group_identifier == 'Pathogenicity':
            return self.prepare_group([self.phylop_100way, self.cadd_scaled, self.revel])
        if group_identifier == 'Splicing':
            return self.prepare_group([self.maxentscan_ref, 
                                       self.maxentscan_alt, 
                                       self.spliceai_details, 
                                       self.spliceai_max_delta, 
                                       self.hexplorer, 
                                       self.hexplorer_wt, 
                                       self.hexplorer_mut, 
                                       self.hexplorer_rev, 
                                       self.hexplorer_rev_wt, 
                                       self.hexplorer_rev_mut, 
                                       self.max_hbond, 
                                       self.max_hbond_wt, 
                                       self.max_hbond_mut, 
                                       self.max_hbond_rev, 
                                       self.max_hbond_rev_wt, 
                                       self.max_hbond_rev_mut])
        if group_identifier == 'gnomAD':
            return self.prepare_group([self.gnomad_ac, 
                                       self.gnomad_af, 
                                       self.gnomad_hom, 
                                       self.gnomad_hemi, 
                                       self.gnomad_het, 
                                       self.gnomad_popmax, 
                                       self.gnomadm_ac_hom, 
                                       self.gnomad_popmax_AF])
        if group_identifier == 'FLOSSIES':
            return self.prepare_group([self.flossies_num_afr, self.flossies_num_eur])
        if group_identifier == 'Cancerhotspots':
            return self.prepare_group([self.cancerhotspots_cancertypes, self.cancerhotspots_af, self.cancerhotspots_ac])
        if group_identifier == 'TP53database':
            return self.prepare_group([self.tp53db_bayes_del, 
                                       self.tp53db_class, 
                                       self.tp53db_DNE_class, 
                                       self.tp53db_DNE_LOF_class, 
                                       self.tp53db_domain_function, 
                                       self.tp53db_transactivation_class])
        if group_identifier == 'HerediCare':
            return self.prepare_group([self.heredicare_cases_count, self.heredicare_family_count])

    def prepare_group(self, group):
        prepared_group = [x for x in group if x is not None]
        if len(prepared_group) == 0:
            return None
        return prepared_group

    def get_spliceai(self):
        return self.spliceai_details, self.spliceai_max_delta
    
    def get_cancerhotspots(self):
        return self.cancerhotspots_cancertypes

    def get_hexplorer(self):
        return self.hexplorer, self.hexplorer_wt, self.hexplorer_mut

    def get_hexplorer_rev(self):
        return self.hexplorer_rev, self.hexplorer_rev_wt, self.hexplorer_rev_mut

    def get_max_hbond(self):
        return self.max_hbond, self.max_hbond_wt, self.max_hbond_mut

    def get_max_hbond_rev(self):
        return self.max_hbond_rev, self.max_hbond_rev_wt, self.max_hbond_rev_mut


@dataclass
class Criterium:

    id: str
    name: str
    type: str
    strength: str
    evidence: str

    def display_name(self):
        the_name = self.name.lower()
        fancy_name = self.name + '_' + self.type
        possible_criteria = ['pvs', 'ps', 'pm', 'pp', 'ba', 'bs', 'bp']
        for criterium in possible_criteria:
            if criterium in the_name and self.type != criterium:
                return fancy_name
        return self.name


    #def strength_to_string(self):
    #    print(self.strength)
    #    if self.strength == "very strong pathogenic":
    #        return "vs"
    #    if self.strength == "strong pathogenic":
    #        return "s"
    #    if self.strength == "medium pathogenic":
    #        return "m"
    #    if self.strength == "supporting pathogenic":
    #        return "p"
    #    if self.strength == "stand-alone benign":
    #        return "ba"
    #    if self.strength == "supporting benign":
    #        return "p"
    #    if self.strength == "strong benign":
    #        return "s"


    def to_vcf(self):
        info = "~2B".join([self.name, self.strength, self.evidence]) # sep: +
        return info

    def criterium_to_num(self):
        the_name = self.name.lower()
        if 'pvs' in the_name:
            return 1
        if 'ps' in the_name:
            return 2
        if 'pm' in the_name:
            return 3
        if 'pp' in the_name:
            return 4
        if 'bp' in the_name:
            return 5
        if 'bs' in the_name:
            return 6
        if 'ba' in the_name:
            return 7
        if '1.' in the_name:
            return 5
        if '2.' in the_name:
            return 4
        if '3.' in the_name:
            return 3
        if '4.' in the_name:
            return 2
        if '5.' in the_name:
            return 1

@dataclass
class Scheme:
    id: int
    display_name: str
    type: str
    criteria: Any # list of criterium
    reference: str
    selected_class: str # can be '-' if the type is 'no scheme'

    def get_criteria_sorted(self):
        sorted_criteria = sorted(self.criteria, key=cmp_to_key(self.compare))
        return sorted_criteria
    
    def compare(self, a, b):
        a = a.criterium_to_num()
        b = b.criterium_to_num()
        return a - b
    
    def to_vcf(self):
        info = ""
        criteria_vcf = ''
        for criterium in self.criteria:
            new_criterium_vcf = criterium.to_vcf()
            criteria_vcf = functions.collect_info(criteria_vcf, "", new_criterium_vcf, sep = "~24") # sep: $
        info = "~7C".join([self.display_name, self.selected_class, criteria_vcf]) # sep: |
        return info

@dataclass
class Gene:
    id: int
    symbol: str

@dataclass
class User:
    id: int
    full_name: str
    affiliation: str

@dataclass
class SelectedLiterature:
    id: int
    pmid: int
    text_passage: str

    def to_vcf(self):
        info = "~2B".join([str(self.pmid), self.text_passage]) # sep: +
        return info


@dataclass
class Classification:
    id: int
    type: str
    selected_class: str
    comment: str
    date: str
    submitter: User

    scheme: Scheme
    literature: Any = None # list of selected literature

    def to_json(self):
        return json.dumps(asdict(self))
    def to_dict(self):
        return asdict(self)

    def to_vcf(self, prefix = True, simple = False):
        if not simple:
            key = functions.encode_vcf(self.type)

            scheme_criteria_vcf = self.scheme.to_vcf()
            text_passage_vcf = ""
            if self.literature is not None:
                for paper in self.literature:
                    current_paper_vcf = paper.to_vcf()
                    text_passage_vcf = functions.collect_info(text_passage_vcf, "", current_paper_vcf, sep = "~24") # sep: $
            cl_vcf = "~7C".join([str(self.selected_class), self.comment, self.date, scheme_criteria_vcf, text_passage_vcf]) # sep: |
            cl_vcf = cl_vcf
            if prefix:
                cl_vcf = key + '~1Y' + cl_vcf
        else:

            cl_vcf = '~3B'.join(['classification~1Y' + str(self.selected_class), 
                                 #'comment~1Y' + self.comment, 
                                 'date~1Y' + self.date, 
                                 'scheme~1Y' + self.scheme.display_name]) # sep: ;
        return cl_vcf
    
    def class_to_text(self, classification = None):
        if classification is None:
            classification = self.selected_class
        classification = str(classification)
        if classification == '1':
            return 'Benign'
        if classification == '2':
            return 'Likely benign'
        if classification in ['3', '3-', '3+']:
            return 'Uncertain significance'
        if classification == '4':
            return 'Likely pathogenic'
        if classification == '5':
            return 'Pathogenic'
        #if classification == '3-':
        #    return 'Uncertain with tendency to benign'
        #if classification == '3+':
        #    return 'Uncertain with tendency to pathogenic'
    
    def get_header(self, simple = False):
        if not simple:
            key = functions.encode_vcf(self.type)
            header = {key: '##INFO=<ID=' + key + ',Number=1,Type=String,Description="The recent consensus classification by the VUS-task-force. Format: consensus_class|consensus_comment|submission_date|consensus_scheme|consensus_scheme_class|consensus_criteria_string. The consensus criteria string itself is a $ separated list with the Format: criterium_name+criterium_strength+criterium_evidence ">\n'}
        else:
            header = {'classification': '##INFO=<ID=classification,Number=1,Type=Integer,Description="The consensus classification from the VUS-task-force. Either 1 (benign), 2 (likely benign), 3 (uncertain), 4 (likely pathogenic) or 5 (pathogenic)">\n',
                      #'comment': '##INFO=<ID=comment,Number=1,Type=String,Description="The comment of the VUS-task-force for the consensus classification">\n',
                      'date': '##INFO=<ID=date,Number=1,Type=String,Description="The date when the consensus classification was submitted. FORMAT: %Y-%m-%d %H:%M:%S">\n',
                      'scheme': '##INFO=<ID=scheme,Number=String,Type=The classification scheme which was used to classify the variant.">\n'}
        return header


@dataclass
class HeredicareClassification:
    id: int
    selected_class: int
    comment: str
    date: str
    center: str

    def to_vcf(self, prefix = True):
        info = '~7C'.join([str(self.selected_class), self.center, self.comment, self.date])
        info = info
        if prefix:
            info = 'heredicare~1Y' + info
        return info

    def get_header(self):
        header = {'heredicare_center_classifications': '##INFO=<ID=heredicare_center_classifications,Number=.,Type=String,Description="An & separated list of the variant classifications from centers imported from HerediCare. Format:class|center|comment|date">\n'}
        return header


@dataclass
class ClinvarCondition:
    condition_id: str
    title: str

@dataclass
class ClinvarSubmission:
    id: int
    interpretation: str
    last_evaluated: str 
    review_status: str
    conditions: Any # list of clinvar conditions
    submitter: str
    comment: str

    def to_vcf(self, prefix = False):
        condition_info = '~24'.join([':'.join([str(submission_condition.condition_id), str(submission_condition.title)]) for submission_condition in self.conditions]) # sep: $
        # as a lot of information in clinvar might be missing it is better to cast every item to str before joining!
        items  = [str(self.interpretation), self.last_evaluated, self.review_status, condition_info, self.submitter, str(self.comment)]
        items = [str(x) for x in items]
        info = '~7C'.join(items) # sep: |
        if prefix:
            info = 'clinvar_submissions~1Y' + info
        return info

@dataclass
class Clinvar:
    id: int
    review_status: str
    interpretation_summary: str
    variation_id: int

    submissions: Any = None # list of clinvar submissions

    def get_header(self):
        headers = {'clinvar_submissions': '##INFO=<ID=clinvar_submissions,Number=.,Type=String,Description="An & separated list of clinvar submissions. Format:interpretation|last_evaluated|review_status|submission_condition|submitter|comment">\n',
                   'clinvar_summary': '##INFO=<ID=clinvar_summary,Number=.,Type=String,Description="summary of the clinvar submissions. FORMAT: review_status:interpretation_summary">\n',
                   'variation_id': '##INFO=<ID=variation_id,Number=1,Type=Integer,Description="The ClinVar variation id of the variant.">\n'
                   }
        return headers

    def to_vcf(self, prefix = True):
        submissions_vcf = functions.process_multiple(self.submissions)
        variation_id_vcf = str(self.variation_id)
        summary_vcf = self.review_status + ':' + self.interpretation_summary
        if prefix:
            variation_id_vcf =  'variation_id~1Y' + variation_id_vcf
            summary_vcf = 'clinvar_summary~1Y' + summary_vcf
        return '~3B'.join([variation_id_vcf, summary_vcf, submissions_vcf])


@dataclass
class Consequence:
    transcript: str
    hgvs_c: str
    hgvs_p: str
    consequence: str
    impact: str
    exon: int
    intron: int

    gene: Gene

    protein_domain_title: str
    protein_domain_id: str

    is_gencode_basic: bool
    is_mane_select: bool
    is_mane_plus_clinical: bool
    is_ensembl_canonical: bool

    source: str
    length: int

    biotype: str

    def get_header(self):
        header = {'variant_consequences': '##INFO=<ID=consequences,Number=.,Type=String,Description="An & separated list of variant consequences from vep. Format:Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical">\n'}
        return header

    def to_vcf(self, prefix = True):
        #Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical
        items = [self.transcript, self.hgvs_c, self.hgvs_p, self.consequence, self.impact, self.exon, self.intron, self.gene.symbol, self.protein_domain_title, self.is_gencode_basic, self.is_mane_select, self.is_mane_plus_clinical, self.is_ensembl_canonical]
        items = [str(x) for x in items]
        info = '~7C'.join(items)
        if prefix:
            info = 'consequences~1Y' + info
        return info

    def get_num_flags(self):
        all_flags = [self.is_gencode_basic, self.is_ensembl_canonical, self.is_mane_select, self.is_mane_plus_clinical]
        prepared_group = [x for x in all_flags if x is not None]
        return sum(prepared_group)
    

@dataclass
class Assay:
    id: int
    type: str
    score: Any
    date: str

    def get_header(self):
        header = {'assays': '##INFO=<ID=assays,Number=.,Type=String,Description="All types of assays (e. g. functional or splicing) which were submitted to HerediVar. Assays are separated by "&" symbols. Format:date|assay_type|score.">\n'}
        return header

    def to_vcf(self, prefix = True):
        info = '~7C'.join([str(self.date), self.type, str(self.score)]) # sep: |
        if prefix:
            info = 'assays~1Y' + info
        return info


@dataclass
class Paper:
    year: int
    authors: str
    title: str
    journal: str
    pmid: int
    source: str

    def get_header(self):
        header = {'literature': '##INFO=<ID=pubmed,Number=.,Type=String,Description="An & separated list of pubmed ids relevant for this variant.">\n'}
        return header

    def to_vcf(self, prefix = True):
        info = str(self.pmid)
        if prefix:
            info = 'literature~1Y' + info
        return info


@dataclass
class Variant:
    id: int
    chrom: str
    pos: int
    ref: str
    alt: str

    is_hidden: bool

    consensus_classifications: Any = None # list of classifications
    user_classifications: Any = None # list of classifications
    heredicare_classifications: Any = None # list of heredicare classifications
    clinvar: Any = None # a clinvar object
    consequences: Any = None # list of consequences
    assays: Any = None # list of assays
    literature: Any = None # list of papers

    annotations: AllAnnotations = AllAnnotations()

    def get_unique_genes(self):
        result = []
        gene_ids = []
        if self.consequences is not None:
            for consequence in self.consequences:
                if consequence.gene.id not in gene_ids and consequence.gene.id is not None:
                    result.append(consequence.gene)
                    gene_ids.append(consequence.gene.id)
        return result

    def to_vcf(self, simple = False):
        headers = {} # collects all headers 
        info = [] # collects info for the headers

        if not simple:
            # standard annotations
            new_header, new_info = self.annotations.to_vcf()
            headers.update(new_header)
            info.extend(new_info)

            # complex annotations
            annotations_oi = [self.user_classifications, 
                              self.heredicare_classifications, 
                              self.consequences, 
                              self.assays, 
                              self.literature,
                              [self.get_recent_consensus_classification()],
                              [self.clinvar]]
            for annot in annotations_oi:
                if annot is not None and annot[0] is not None:
                    new_info = functions.process_multiple(annot)
                    info.append(new_info)
                    new_header = annot[0].get_header()
                    headers.update(new_header)

        elif simple:
            # only collect consensus classification
            annot = self.get_recent_consensus_classification()
            if annot is not None:
                new_info = annot.to_vcf(simple = simple)
                info.append(new_info)
                new_header = annot.get_header(simple = simple)
                headers.update(new_header)

        # prepate complete vcf line
        #"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
        info = '~3B'.join(info) # sep: ;
        info = functions.encode_vcf(info)
        if info.strip() == '':
            info = '.'
        variant_vcf = '\t'.join((self.chrom, str(self.pos), str(self.id), self.ref, self.alt, '.', '.', info))
        #print(headers)
        #print(variant_vcf)
        return headers, variant_vcf
    

    def get_user_classifications(self, user_id):
        result = []
        if self.user_classifications is not None:
            for classification in self.user_classifications:
                if classification.submitter.id == user_id:
                    result.append(classification)
        return result


    #def get_annotation_keys(self):
    #    return ['annotations', 'consensus_classifications', 'user_classifications', 'heredicare_classifications', 'clinvar', 'assays', 'literature']
    
    def to_json(self):
        return json.dumps(asdict(self))

    def get_recent_consensus_classification(self):
        result = None
        if self.consensus_classifications is not None:
            for classification in self.consensus_classifications:
                if result is None:
                    result = classification
                else:
                    if classification.date > result.date:
                        result = classification
        return result
    
    def get_recent_consensus_classification_all_schemes(self, convert_to_dict = False):
        result = None
        if self.consensus_classifications is not None:
            result = {}
            for classification in self.consensus_classifications:
                current_scheme_id = classification.scheme.id
                if current_scheme_id not in result:
                    result[current_scheme_id] = classification
                elif classification.date > result[current_scheme_id].date:
                    result[current_scheme_id] = classification # update if the current classification is newer
        if convert_to_dict and result is not None:
            return {scheme_id:classification.to_dict() for scheme_id, classification in result.items()}
        return result
                    



    def get_recent_user_classification(self, user_id = 'all', scheme_id = 'all'):
        result = None
        if self.user_classifications is not None:
            for classification in self.user_classifications:
                if (classification.submitter.id == user_id or user_id == 'all') and (classification.scheme.id == scheme_id or scheme_id == 'all'):
                    if result is None: # the first classification for this user seen
                        result = classification
                    else:
                        if classification.date > result.date: # current classification is newer than the saved one
                            result = classification
        return result

    def get_genes(self, how = "object"):
        result = None
        if self.consequences is not None:
            result = []
            gene_ids = []
            for consequence in self.consequences:
                current_gene = consequence.gene
                if current_gene is not None:
                    if current_gene.id not in gene_ids and current_gene.id is not None:
                        result.append(current_gene)
                        gene_ids.append(current_gene.id)
        if how == "string":
            result = '~3B'.join([g.symbol for g in result])
        return result


    # this function returns a list of consequence objects of the preferred transcripts 
    # (can be multiple if there are eg. 2 mane select transcripts for this variant)
    def get_preferred_transcripts(self):
        result = []
        consequences = self.consequences

        if consequences is None:
            return None

        consequences = [c for c in consequences if c.source == 'ensembl'] # filter for ensembl transcripts
        if len(consequences) > 0:
            consequences = self.order_consequences(consequences)
            result.append(consequences.pop(0)) # always append the first one

            for consequence in consequences: # scan for all mane select transcripts
                if consequence.is_mane_select:
                    result.append(consequence)
                else:
                    break # we can do this because the list is sorted
        else: # the variant does not have any consequences
            return None
        return result

    def order_consequences(self, consequences):
        keyfunc = cmp_to_key(mycmp = self.sort_consequences)
        consequences.sort(key = keyfunc) # sort by preferred transcript
        return consequences
     
    def sort_consequences(self, a:Consequence, b:Consequence):
        # sort by ensembl/refseq
        if a.source == 'ensembl' and b.source == 'refseq':
            return -1
        elif a.source == 'refseq' and b.source == 'ensembl':
            return 1
        elif a.source == b.source:

            # sort by mane select
            if a.is_mane_select is None or b.is_mane_select is None:
                return 1
            elif a.is_mane_select and not b.is_mane_select:
                return -1
            elif not a.is_mane_select and b.is_mane_select:
                return 1
            elif a.is_mane_select == b.is_mane_select:

                # sort by biotype
                if a.biotype == 'protein coding' and b.biotype != 'protein coding':
                    return -1
                elif a.biotype != 'protein coding' and b.biotype == 'protein coding':
                    return 1
                elif (a.biotype != 'protein coding' and b.biotype != 'protein coding') or (a.biotype == 'protein coding' and b.biotype == 'protein coding'):

                    # sort by length
                    if a.length > b.length:
                        return -1
                    elif a.length < b.length:
                        return 1
                    else:
                        return 0
                    

import datetime

@dataclass
class import_request:
    id: int
    user: User
    requested_at: datetime.datetime
    status: str
    finished_at: datetime.datetime

    import_variant_list_status: str
    import_variant_list_finished_at: datetime.datetime
    import_variant_list_message: str
    variant_summary: dict

@dataclass
class Import_variant_request:
    id: int
    status: str
    requested_at: datetime.datetime
    finished_at: datetime.datetime
    message: str
    vid: str