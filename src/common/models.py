from dataclasses import dataclass, asdict, fields
import json
from typing import Any
import common.functions as functions
from functools import cmp_to_key
import datetime
from abc import ABC, abstractmethod
import math

@dataclass 
class AbstractDataclass(ABC): 
    def __new__(cls, *args, **kwargs): 
        if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass: 
            raise TypeError("Cannot instantiate abstract class.") 
        return super().__new__(cls)

@dataclass
class Abstract_Annotation(AbstractDataclass):
    id: int
    value: Any
    
    title: str
    display_title: str
    description: str
    version: str
    version_date: str
    value_type: str

    group_name: str

    draw: bool = True

    is_transcript_specific: bool = False

    @abstractmethod
    def to_vcf(self, prefix = True):
        pass

    @abstractmethod
    def get_header(self):
        pass


@dataclass
class CancerhotspotsAnnotation(Abstract_Annotation):
    # value = cancertype
    oncotree_symbol: str = None
    tissue: str = None
    occurances: int = None

    def to_vcf(self, prefix = True):
        # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        data = [self.oncotree_symbol, self.value, self.tissue, self.occurances]
        data = [str(x) for x in data]
        data = '~7C'.join(data)
        if prefix:
            data = self.title + '~1Y' + data
        return data
    
    def get_header(self): # TODO
        header = {self.title: '##INFO=<ID=' + self.title + ',Number=1,Type=String,Description="' + self.description + '. An & separated list of cancerhotspots annotations. Each annotation has the FORMAT: oncotree_symbol|cancertype|tissue|num_occurances. (version: ' + str(self.version) +  ', version date: ' + str(self.version_date) + ' )">\n'}
        return header 


@dataclass
class Annotation(Abstract_Annotation):
    def get_value(self):
        if self.value_type == 'text':
            return str(self.value)
        if self.value_type == 'int':
            return int(self.value)
        if self.value_type == 'float':
            return float(self.value)
        return self.value
    
    def to_vcf(self, prefix = True):
        data_base = ""
        if prefix:
            data_base = self.title + '~1Y'
        data = data_base + self.value
        return data
    
    def get_header(self):
        header = {self.title: '##INFO=<ID=' + self.title + ',Number=1,Type=String,Description="' + self.description + ' (version: ' + str(self.version) +  ', version date: ' + str(self.version_date) + ' )">\n'}
        return header


@dataclass
class TranscriptAnnotation(Abstract_Annotation):
    #value is a transcript -> value dict

    def get_value(self, transcript):
        the_value = self.value[transcript]
        if self.value_type == 'text':
            return str(the_value)
        if self.value_type == 'int':
            return int(the_value)
        if self.value_type == 'float':
            return float(the_value)
        return self.value

    def to_vcf(self, prefix = False):
        value_strings = []
        for transcript in self.value:
            new_value_string = transcript + "~24" + self.value[transcript] # sep: $
            if new_value_string.strip() != "~24":
                value_strings.append(new_value_string)
        data = self.title + '~1Y' + "~7C".join(value_strings)
        return data
    
    def get_header(self):
        header = {self.title: '##INFO=<ID=' + self.title + ',Number=1,Type=String,Description="' + self.description + '. A | separated list of transcript$value pairs. (version: ' + str(self.version) +  ', version date: ' + str(self.version_date) + ' )">\n'}
        return header

    def sort(self):
        transcripts_sorted, values_sorted = functions.sort_transcript_dict(self.value)
        return transcripts_sorted, values_sorted

    def max(self):
        max_val = None
        max_transcript = None
        for current_transcript in self.value:
            current_value = self.get_value(current_transcript)
            if max_val is None:
                max_val = current_value
                max_transcript = current_transcript
            elif max_val < current_value:
                max_val = current_value
                max_transcript = current_transcript
        return max_transcript, max_val


@dataclass
class AllAnnotations:
    rsid: Annotation = None

    phylop_100way: Annotation = None
    cadd_scaled: Annotation = None
    revel: TranscriptAnnotation = None
    
    spliceai_details: Annotation = None
    spliceai_max_delta: Annotation = None
    maxentscan_ref: Annotation = None
    maxentscan_alt: Annotation = None
    maxentscan: TranscriptAnnotation = None
    maxentscan_swa: TranscriptAnnotation = None

    gnomad_ac: Annotation = None
    gnomad_af: Annotation = None
    gnomad_hom: Annotation = None
    gnomad_hemi: Annotation = None
    gnomad_het: Annotation = None
    gnomad_popmax: Annotation = None
    gnomadm_ac_hom: Annotation = None
    gnomad_popmax_AF: Annotation = None
    gnomad_popmax_AC: Annotation = None

    brca_exchange_clinical_significance: Annotation = None
    arup_classification: Annotation = None
    
    flossies_num_afr: Annotation = None
    flossies_num_eur: Annotation = None
    
    #cancerhotspots_cancertypes: Annotation = None
    cancerhotspots_ac: Annotation = None
    cancerhotspots_af: Annotation = None

    tp53db_class: Annotation = None
    tp53db_DNE_LOF_class: Annotation = None
    #tp53db_bayes_del: Annotation = None
    tp53db_DNE_class: Annotation = None
    tp53db_domain_function: Annotation = None
    tp53db_transactivation_class: Annotation = None

    task_force_protein_domain: Annotation = None
    task_force_protein_domain_source: Annotation = None
    coldspot: Annotation = None

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

    bayesdel: Annotation = None


    def get_all_annotation_names(self):
        return self.__annotations__

    def to_vcf(self):
        headers = {}
        info = []
        for annot in self.get_non_none_annotations():
            data = annot.to_vcf()
            header = annot.get_header()
            headers.update(header)
            info.append(data)
        return headers, info

    def get_non_none_annotations(self):
        return [getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None]

    def flag_linked_annotations(self):
        self.setattr_advanced(self.spliceai_details, 'draw', False)
        self.setattr_advanced(self.spliceai_max_delta, 'draw', False)
        #self.setattr_advanced(self.cancerhotspots_cancertypes, 'draw', False)
        self.setattr_advanced(self.cancerhotspots_ac, 'draw', False)
        self.setattr_advanced(self.cancerhotspots_af, 'draw', False)
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
        result = set()
        for current_field in fields(self):
            current_annotation = getattr(self, current_field.name)
            if current_annotation is not None:
                current_group_name = current_annotation.group_name
                if str(current_group_name) != "None":
                    result.add(current_group_name)
        return list(result) # ['Pathogenicity', 'Splicing', 'gnomAD', 'FLOSSIES', 'Cancerhotspots', 'TP53database', 'HerediCare', 'Protein Domain']

    def get_group(self, group_identifier):
        result = []
        for current_field in fields(self):
            current_annotation = getattr(self, current_field.name)
            if current_annotation is not None:
                current_group_name = current_annotation.group_name
                if current_group_name is not None:
                    if current_group_name == group_identifier:
                        result.append(current_annotation)
        return self.prepare_group(result)

    def prepare_group(self, group):
        prepared_group = [x for x in group if x is not None]
        if len(prepared_group) == 0:
            return None
        return prepared_group

    def get_spliceai(self):
        return self.spliceai_details, self.spliceai_max_delta
    
    #def get_cancerhotspots(self):
    #    return self.cancerhotspots_cancertypes

    def get_hexplorer(self):
        return self.hexplorer, self.hexplorer_wt, self.hexplorer_mut

    def get_hexplorer_rev(self):
        return self.hexplorer_rev, self.hexplorer_rev_wt, self.hexplorer_rev_mut

    def get_max_hbond(self):
        return self.max_hbond, self.max_hbond_wt, self.max_hbond_mut

    def get_max_hbond_rev(self):
        return self.max_hbond_rev, self.max_hbond_rev_wt, self.max_hbond_rev_mut

@dataclass
class Criterium(AbstractDataclass):
    id: int
    name: str
    type: str
    strength: str
    evidence: str
    state: str

    def to_dict(self):
        return asdict(self)

@dataclass
class HerediVarCriterium(Criterium):
    """
    id: int
    name: str
    type: str
    strength: str
    evidence: str
    state: str
    """
    strength_display_name: str

    def display_name(self):
        the_name = self.name.lower()
        fancy_name = self.name + '_' + self.strength_display_name
        possible_criteria = ['pvs', 'ps', 'pm', 'pp', 'ba', 'bs', 'bp']
        for criterium in possible_criteria:
            if criterium in the_name and self.type != criterium:
                return fancy_name
        return self.name

    def to_vcf(self):
        info = "~2B".join([self.name, self.strength, self.evidence, self.state,]) # sep: +
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

    is_active: bool
    is_default: bool

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
    
    def get_comment_display(self):
        if self.comment == '':
            return "None"
        return self.comment
    
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
        if classification == '3-':
            return 'Uncertain significance'
        if classification == '3+':
            return 'Uncertain significance'
        if classification == '4M':
            return 'Likely pathogenic, low penetrance'

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
                                 'comment~1Y' + self.comment, 
                                 'date~1Y' + self.date, 
                                 'scheme~1Y' + self.scheme.display_name,
                                 'source~1Y' + "heredivar"]) # sep: ;
        return cl_vcf
    
    def get_header(self, simple = False):
        if not simple:
            key = functions.encode_vcf(self.type)
            header = {key: '##INFO=<ID=' + key + ',Number=1,Type=String,Description="The recent consensus classification by the VUS-task-force. Format: consensus_class|consensus_comment|submission_date|consensus_scheme|consensus_scheme_class|consensus_criteria_string. The consensus criteria string itself is a $ separated list with the Format: criterium_name+criterium_strength+criterium_evidence+state ">\n'}
        else:
            header = {'classification': '##INFO=<ID=classification,Number=1,Type=Integer,Description="The consensus classification from the VUS-task-force. Either 1 (benign), 2 (likely benign), 3 (uncertain), 4 (likely pathogenic) or 5 (pathogenic)">\n',
                      'comment': '##INFO=<ID=comment,Number=1,Type=String,Description="The comment of the VUS-task-force for the consensus classification">\n',
                      'date': '##INFO=<ID=date,Number=1,Type=String,Description="The date when the consensus classification was submitted. FORMAT: %Y-%m-%d %H:%M:%S">\n',
                      'scheme': '##INFO=<ID=scheme,Number=1,Type=String,Description="The classification scheme which was used to classify the variant.">\n',
                      'source': '##INFO=<ID=source,Number=1,Type=String,Description="The source of the classification. Either heredivar or heredicare">\n'}
        return header

@dataclass
class AutomaticClassificationCriterium(Criterium):
    """
    id: int
    name: str
    type: str
    strength: str
    evidence: str
    state: str
    """
    rule_type: str # general/splicing/proteion
    evidence_type: str # pathogenic/benign

    def display_name(self):
        return self.name.replace('protein', 'prt').replace('splicing', 'spl')
    
    def to_vcf(self):
        #criterium_name+criterium_strength+criterium_evidence+state+rule_type
        return "~2B".join([
            self.name,
            self.strength,
            self.evidence,
            self.state,
            self.rule_type
        ])


@dataclass
class AutomaticClassification:
    id: int
    scheme_id: int
    scheme_display_title: str
    classification_splicing: int
    classification_protein: int
    date: datetime

    criteria: Any # list of automatic classification criterium

    def filter_criteria(self, rule_type):
        result = []
        if self.criteria is not None:
            for criterium in self.criteria:
                if criterium.rule_type == 'general' or criterium.rule_type == rule_type: # always keep general criteria
                    result.append(criterium)
        return result
    
    def to_dict(self):
        return asdict(self)
    
    def to_vcf(self, prefix = True):
        # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        criteria_str = '~24'.join([criterium.to_vcf() for criterium in self.criteria])
        info = '~7C'.join([
            self.classification_protein,
            self.classification_splicing,
            self.date.strftime('%Y-%m-%d %H:%M:%S'),
            self.scheme_display_title,
            criteria_str
        ])
        if prefix:
            info = 'automatic_classification~1Y' + info
        return info
    
    def get_header(self):
        #consensus_class|consensus_comment|submission_date|consensus_scheme|consensus_scheme_class|consensus_criteria_string. The consensus criteria string itself is a $ separated list with the Format: criterium_name+criterium_strength+criterium_evidence
        header = {
            'automatic_classification': '##INFO=<ID=automatic_classification,Number=1,Type=String,Description="The automatic classification for this variant. FORMAT: classification_protein|classification_splicing|date|scheme|criteria. criteria is a $ separated list with the FORMAT: criterium_name+criterium_strength+criterium_evidence+state+rule_type">\n',
        }
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
                   'clinvar_summary': '##INFO=<ID=clinvar_summary,Number=.,Type=String,Description="summary of the clinvar submissions. FORMAT: review_status:interpretation_summary">\n'
                   }
        return headers

    def to_vcf(self, prefix = True):
        if self.submissions is not None:
            submissions_vcf = functions.process_multiple(self.submissions)
        else:
            submissions_vcf = "clinvar_submissions~1YNone"
        summary_vcf = self.review_status + ':' + self.interpretation_summary
        if prefix:
            summary_vcf = 'clinvar_summary~1Y' + summary_vcf
        return '~3B'.join([summary_vcf, submissions_vcf])


@dataclass
class Transcript:
    id: int
    gene: Gene
    name: str
    biotype: str
    length: int
    chrom: str
    start: int
    end: int
    orientation: str
    source: str

    is_gencode_basic: bool
    is_mane_select: bool
    is_mane_plus_clinical: bool
    is_ensembl_canonical: bool

    def get_total_flags(self):
        return self.is_gencode_basic + self.is_mane_select + self.is_mane_plus_clinical + self.is_ensembl_canonical

@dataclass
class Consequence:
    transcript: Transcript
    hgvs_c: str
    hgvs_p: str
    consequence: str
    impact: str
    exon: str
    intron: str

    protein_domain_title: str
    protein_domain_id: str

    def get_header(self):
        header = {'variant_consequences': '##INFO=<ID=consequences,Number=.,Type=String,Description="An & separated list of variant consequences from vep. Format:Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical|transcript_biotype|transcript_length">\n'}
        return header

    def to_vcf(self, prefix = True):
        #Transcript|hgvsc|hgvsp,consequence|impact|exonnr|intronnr|genesymbol|proteindomain|isgencodebasic|ismaneselect|ismaneplusclinical|isensemblcanonical
        items = [self.transcript.name, self.hgvs_c, self.hgvs_p, self.consequence, self.impact, self.exon, self.intron, self.transcript.gene.symbol, self.protein_domain_title, self.transcript.is_gencode_basic, self.transcript.is_mane_select, self.transcript.is_mane_plus_clinical, self.transcript.is_ensembl_canonical, self.transcript.biotype, self.transcript.length]
        items = [str(x) for x in items]
        info = '~7C'.join(items)
        if prefix:
            info = 'consequences~1Y' + info
        return info

    def get_num_flags(self):
        all_flags = [self.transcript.is_gencode_basic, self.transcript.is_ensembl_canonical, self.transcript.is_mane_select, self.transcript.is_mane_plus_clinical]
        prepared_group = [x for x in all_flags if x is not None]
        return sum(prepared_group)


@dataclass
class Assay_Metadata_Type:
    id: int
    title: str
    display_title: str
    assay_type_id: int
    value_type: str
    is_deleted: bool
    is_required: bool

@dataclass
class Assay_Metadata:
    id: int
    metadata_type: Assay_Metadata_Type
    value: str


@dataclass
class Assay:
    id: int
    assay_type_id: int
    type_title: str
    date: str
    link: str

    metadata: Any # dict of Assay Metadata

    def get_header(self):
        ## Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        header = {'assays': '##INFO=<ID=assays,Number=.,Type=String,Description="All types of assays (e. g. functional or splicing) which were submitted to HerediVar. Assays are separated by "&" symbols. Format:assay_type|date|link|metadata. Metadata itself is a $ separated list of key+value pairs.">\n'}
        return header

    def to_vcf(self, prefix = True):
        metadata_parts = []
        for assay_metadata_title in self.metadata:
            assay_metadata = self.metadata[assay_metadata_title]
            new_element = "~2B".join([assay_metadata.metadata_type.display_title, assay_metadata.value])
            metadata_parts.append(new_element)
        metadata = "~24".join(metadata_parts)
        info = '~7C'.join([self.type_title, str(self.date), str(self.link), metadata]) # sep: |
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
class AbstractHeredicareClassification(AbstractDataclass):
    id: int
    selected_class: int
    comment: str


    def selected_class_to_text(self):
        if self.selected_class is None:
            return "not classified"
        class2text = {
            "1": "pathogenic",
            "2": "VUS",
            "3": "polymorphism/neutral",
            "11": "class 1",
            "12": "class 2",
            "32": "class 3-",
            "13": "class 3",
            "34": "class 3+",
            "14": "class 4",
            "15": "class 5",
            "20": "artifact",
            "21": "not classified",
            "4": "unknown",
            "-1": "not classified"
        }
        return class2text[str(self.selected_class)]
    
    def selected_class_to_num(self):
        if self.selected_class is None:
            return "-"
        class2text = {
            "1": "5",
            "2": "3",
            "3": "1",
            "11": "1",
            "12": "2",
            "32": "3-",
            "13": "3",
            "34": "3+",
            "14": "4",
            "15": "5",
            "20": "-", # ARTIFACT???
            "21": "-",
            "4": "-",
            "-1": "-"
        }
        return class2text[str(self.selected_class)]
    
    @abstractmethod
    def to_vcf(self):
        pass

    @abstractmethod
    def get_header(self):
        pass


    
@dataclass
class HeredicareConsensusClassification(AbstractHeredicareClassification):
    classification_date: str

    def to_vcf(self, prefix = True, simple = False):
        if not simple:
            comment = "" if self.comment is None else self.comment
            date = "" if self.classification_date is None else self.classification_date.strftime('%Y-%m-%d')
            info = '~2B'.join([self.selected_class_to_num(), comment, date])
            info = info
            if prefix:
                info = 'heredicare_consensus_classifications~1Y' + info
        else:
            info = ['classification~1Y' + self.selected_class_to_num(), 
                    #'comment~1Y' + self.comment, 
                ]
            if self.classification_date is not None:
                info.append('date~1Y' + self.classification_date.strftime("%Y-%m-%d %H:%M:%S"))
            info.append('source~1Y' + "heredicare")
            info = '~3B'.join(info) # sep: ;
        return info

    def get_header(self, simple = False):
        if not simple:
            header = {'heredicare_consensus_classifications': '##INFO=<ID=heredicare_consensus_classifications,Number=.,Type=String,Description="An & separated list of the consensus classification imported from HerediCare. Format:class&comment&date">\n'}
        else:
            header = {'classification': '##INFO=<ID=classification,Number=1,Type=Integer,Description="The consensus classification from the VUS-task-force. Either 1 (benign), 2 (likely benign), 3 (uncertain), 4 (likely pathogenic) or 5 (pathogenic)">\n',
                      #'comment': '##INFO=<ID=comment,Number=1,Type=String,Description="The comment of the VUS-task-force for the consensus classification">\n',
                      'date': '##INFO=<ID=date,Number=1,Type=String,Description="The date when the consensus classification was submitted. FORMAT: %Y-%m-%d %H:%M:%S">\n',
                      'source': '##INFO=<ID=source,Number=1,Type=String,Description="The source of the classification. Either heredivar or heredicare">\n'}
        return header
    
@dataclass
class HeredicareCenterClassification(AbstractHeredicareClassification):
    center_name: str
    zid: int

    def to_vcf(self, prefix = True):
        ## Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        comment = "" if self.comment is None else comment
        info = "~2B".join([self.center_name, str(self.zid), self.selected_class_to_num(), comment])
        if prefix:
            info = "heredicare_center_classifications~1Y" + info
        return info

    def get_header(self):
        header = {'heredicare_center_classifications': '##INFO=<ID=heredicare_center_classifications,Number=.,Type=String,Description="An & separated list of the consensus classification imported from HerediCare. Format:center_name|zid|class|comment">\n'}
        return header

    
    
@dataclass
class HeredicareAnnotation:
    id: int
    vid: str
    n_fam: int
    n_pat: int
    consensus_classification: HeredicareConsensusClassification # kind of ugly to use that here because to_vcf can not be used as this is used for the center classifications...

    lr_cooc: float
    lr_coseg: float
    lr_family: float

    center_classifications: Any # list of HerediCareCenterClassification objects

    def get_centers_with_classifications(self):
        center_classifications = self.center_classifications
        result = None
        if center_classifications is not None:
            result = []
            for center_classification in center_classifications:
                if center_classification.selected_class is not None:
                    result.append(center_classification.center_name)
        return result

    def to_vcf(self, prefix = True):
        consensus_comment = "" if self.consensus_classification.comment is None else self.consensus_classification.comment
        consensus_date = "" if self.consensus_classification.classification_date is None else self.consensus_classification.classification_date.strftime('%Y-%m-%d')
        center_specific_vcf = functions.process_multiple(self.center_classifications, sep="~24", do_prefix = False)
        heredicare_annotation_vcf = "~7C".join([str(x) for x in [self.vid, self.n_fam, self.n_pat, self.lr_cooc, self.lr_coseg, self.lr_family, self.consensus_classification.selected_class_to_num(), consensus_comment, consensus_date, center_specific_vcf]])
        if prefix:
            heredicare_annotation_vcf = "heredicare_annotation~1Y" + heredicare_annotation_vcf
        return heredicare_annotation_vcf

    
    # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
    def get_header(self):
        header = {'heredicare_annotation': '##INFO=<ID=heredicare_annotation,Number=.,Type=String,Description="An & separated list of the variant annotations from heredicare. Format:vid|n_fam|n_pat|lr_cooc|lr_coseg|lr_family|consensus_classification_class|consensus_classification_comment|consensus_classification_date|center_specific_classifications. center_specific_classifications is a $ seperated list with FORMAT: center_name+zid+class+comment">\n'}
        return header



@dataclass
class AbstractVariant(AbstractDataclass):
    id: int # variant_id
    is_hidden: bool
    variant_type: str

    chrom: str
    pos: int
    ref: str
    alt: str

    imprecise: bool = False

    consensus_classifications: Any = None # list of classifications
    user_classifications: Any = None # list of classifications
    automatic_classification: AutomaticClassification = None
    heredicare_annotations: Any = None # list of heredicare annotatins
    clinvar: Any = None # a clinvar object
    consequences: Any = None # list of consequences
    assays: Any = None # list of assays
    literature: Any = None # list of papers
    cancerhotspots_annotations: Any = None # list of cancerhotspotsAnnotations

    annotations: AllAnnotations = AllAnnotations()

    external_ids: Any = None # list of Annotations

    def order_assays_by_type(self):
        # dict of assay_type title -> assay
        result = {}
        if self.assays is not None:
            for assay in self.assays:
                result = functions.extend_dict(result, assay.type_title, assay)
        return result

    def get_external_ids(self, title):
        result = []
        if self.external_ids is not None:
            for external_id in self.external_ids:
                if external_id.title == title:
                    result.append(external_id)
        return result
    
    def group_external_ids(self):
        result = {}
        if self.external_ids is not None:
            for external_id in self.external_ids:
                current_source = external_id.title
                functions.extend_dict(result, current_source, external_id)
        return result

    def get_heredicare_consensus_classifications(self):
        result = []
        for heredicare_annotation in self.heredicare_annotations:
            if heredicare_annotation.consensus_classification.selected_class is not None:
                result.append(heredicare_annotation.consensus_classification)
        return result

    def get_total_heredicare_counts(self):
        total_n_fam = 0
        total_n_pat = 0
        if self.heredicare_annotations is not None:
            for annot in self.heredicare_annotations:
                total_n_fam += annot.n_fam
                total_n_pat += annot.n_pat
        return total_n_fam, total_n_pat
    
    def get_best_lr_scores(self):
        lr_cooc = None
        lr_coseg = None
        lr_family = None
        if self.heredicare_annotations is not None:
            for annot in self.heredicare_annotations:
                if annot.lr_coseg is not None:
                    if lr_coseg is None or abs(math.log10(annot.lr_coseg)) > abs(math.log10(lr_coseg)):
                        lr_coseg = annot.lr_coseg
                if annot.lr_cooc is not None:
                    if lr_cooc is None or abs(math.log10(annot.lr_cooc)) > abs(math.log10(lr_cooc)):
                        lr_cooc = annot.lr_cooc
                if annot.lr_family is not None:
                    if lr_family is None or abs(math.log10(annot.lr_family)) > abs(math.log10(lr_family)):
                        lr_family = annot.lr_family
        return lr_cooc, lr_coseg, lr_family

    def get_user_classifications(self, user_id):
        result = []
        if self.user_classifications is not None:
            for classification in self.user_classifications:
                if classification.submitter.id == user_id:
                    result.append(classification)
        return result

    def to_json(self):
        return json.dumps(asdict(self))



    def get_most_recent_heredicare_consensus_classification(self):
        result = None
        if self.heredicare_annotations is None:
            return None
        maxdate = datetime.date.min
        for heredicare_annotation in self.heredicare_annotations:
            current_classification = heredicare_annotation.consensus_classification
            if current_classification.selected_class is not None:
                if result is None:
                    result = current_classification
                    if current_classification.classification_date is None:
                        maxdate = datetime.date.min
                    else:
                        maxdate = current_classification.classification_date
                if current_classification.classification_date is not None:
                    if current_classification.classification_date > maxdate:
                        result = current_classification
                        if current_classification.classification_date is not None:
                            maxdate = current_classification.classification_date
                        else:
                            maxdate = datetime.date.min
        return result
    
    # the most recent consensus class or if that does not exist the most recent heredicare consensus classification
    def get_consensus_class(self):
        the_class = "-"
        source = "heredivar"
        most_recent_consensus_classification  = self.get_recent_consensus_classification()
        if most_recent_consensus_classification is None:
            heredicare_classification = self.get_most_recent_heredicare_consensus_classification()
            if heredicare_classification is not None:
                the_class = heredicare_classification.selected_class_to_num()
                source = "heredicare"
        else:
            the_class = most_recent_consensus_classification.selected_class
            source = "heredivar"

        return the_class, source


    # the most recent conensus classification independent of schemes
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
    
    # the most recent consensus classification for each scheme
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
            gene2count = {}
            for consequence in self.consequences:
                current_gene = consequence.transcript.gene
                if current_gene is not None:
                    if current_gene.id is not None:
                        gene_symbol = current_gene.symbol
                        if gene_symbol not in gene2count:
                            gene2count[gene_symbol] = 1
                        else:
                            gene2count[gene_symbol] += 1
                        if current_gene.id not in gene_ids:
                            result.append(current_gene)
                            gene_ids.append(current_gene.id)

        if result is None or len(result) == 0:
            return None
        if how == "string":
            result = '~3B'.join([g.symbol for g in result])
        if how == "list":
            result = [g.symbol for g in result]
        if how == "best":
            result = [g.symbol.upper() for g in result]
            preferred_genes = functions.get_preferred_genes()
            avail_preferred_genes = set(result) & preferred_genes
            if len(avail_preferred_genes) > 0:
                result = list(avail_preferred_genes)
            preferred_genes2count = {x:y for x,y in gene2count.items() if x.upper() in result}
            result = max(preferred_genes2count, key=preferred_genes2count.get)
        return result


    # this function returns a list of consequence objects of the preferred transcripts 
    # (can be multiple if there are eg. 2 mane select transcripts for this variant)
    # this should be renamed to get_preferred_consequences
    def get_preferred_transcripts(self) -> list:
        result = []
        consequences = self.consequences

        if consequences is None:
            return None
        
        sortable_dict = {}
        for consequence in consequences:
            if consequence.transcript.source == 'ensembl':
                sortable_dict[consequence.transcript.name] = consequence

        if len(sortable_dict) == 0:
            return None
        
        transcripts_sorted, consequences_sorted = functions.sort_transcript_dict(sortable_dict)
        
        if len(consequences_sorted) > 0:
            result.append(consequences_sorted.pop(0)) # always append the first one
            for consequence in consequences_sorted: # scan for all mane select transcripts
                if consequence.transcript.is_mane_select:
                    result.append(consequence)
                else:
                    break # we can do this because the list is sorted
        elif len(consequences_sorted) == 0 and '' in sortable_dict:
            return [sortable_dict['']]  # intergenic variant
        else:
            return None

        return result
    
    def get_sorted_consequences(self) -> list:
        consequences = self.consequences
        if consequences is None:
            return None
        
        sortable_dict = {}
        for consequence in consequences:
            if consequence.transcript.source == 'ensembl':
                sortable_dict[consequence.transcript.name] = consequence

        if len(sortable_dict) == 0:
            return None
        
        transcripts_sorted, consequences_sorted = functions.sort_transcript_dict(sortable_dict)

        return consequences_sorted

    @abstractmethod
    def to_vcf(self, simple = False):
        pass

    @abstractmethod
    def get_string_repr(self):
        pass

@dataclass
class Variant(AbstractVariant):
    def to_vcf(self, simple = False):
        # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        headers = {} # collects all headers 
        info = [] # collects info for the headers

        if not simple:
            # standard annotations
            new_header, new_info = self.annotations.to_vcf()
            headers.update(new_header)
            info.extend(new_info)

            # external ids
            external_id_groups = self.group_external_ids()
            for external_id_group in external_id_groups:
                add_title = True
                new_info_collection = []
                for external_id in external_id_groups[external_id_group]:
                    new_info = external_id.to_vcf(add_title)
                    new_header = external_id.get_header()
                    headers.update(new_header)
                    new_info_collection.append(new_info)
                    add_title = False
                if len(new_info_collection) > 0:
                    info.append("~26".join(new_info_collection)) # sep &

            # complex annotations
            annotations_oi = [self.user_classifications,
                              [self.get_recent_consensus_classification()],
                              [self.automatic_classification],
                              [self.clinvar],
                              self.heredicare_annotations,
                              self.consequences, 
                              self.assays, 
                              self.literature,
                              self.cancerhotspots_annotations
                            ]
            for annot in annotations_oi:
                if annot is not None:
                    if len(annot) > 0:
                        if annot[0] is not None:
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
            else:
                annot = self.get_most_recent_heredicare_consensus_classification()
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
    
    def get_string_repr(self):
        return '-'.join([self.chrom, str(self.pos), self.ref, self.alt])


@dataclass
class Custom_Hgvs():
    id: int
    transcript: str
    hgvs: str
    hgvs_type: str

@dataclass
class SV_Variant(AbstractVariant):
    sv_variant_id: int = None
    start: int = None
    end: int = None
    sv_type: str = None

    custom_hgvs: Any = None # a list of custom hgvs objects

    overlapping_genes: Any = None # list of lists with: gene_id, gene name, min(start), max(end)

    def __post_init__(self):
        if any([x is None for x in [self.sv_variant_id, self.chrom, self.start, self.end, self.sv_type, self.imprecise]]):
            raise ValueError("Some arguments are missing")

    def to_vcf(self, simple = False):
        # Separator-symbol-hierarchy: ; -> & -> | -> $ -> +
        headers = {} # collects all headers 
        info = [] # collects info for the headers

        # first add information for structural variants
        headers["START"] = '##INFO=<ID=START,Number=1,Type=Integer,Description="Start position of the variant described in this record">'
        info.append("START~1Y" + str(self.start))
        headers["END"] = '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">'
        info.append("END~1Y" + str(self.end))
        headers["SVTYPE"] = '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">'
        info.append("SVTYPE~1Y" + self.sv_type)
        if self.imprecise:
            headers["IMPRECISE"] = '##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description="Imprecise structural variation">'
            info.append("IMPRECISE")

        if not simple:
            # standard annotations
            new_header, new_info = self.annotations.to_vcf()
            headers.update(new_header)
            info.extend(new_info)

            # external ids
            external_id_groups = self.group_external_ids()
            for external_id_group in external_id_groups:
                add_title = True
                new_info_collection = []
                for external_id in external_id_groups[external_id_group]:
                    new_info = external_id.to_vcf(add_title)
                    new_header = external_id.get_header()
                    headers.update(new_header)
                    new_info_collection.append(new_info)
                    add_title = False
                if len(new_info_collection) > 0:
                    info.append("~26".join(new_info_collection)) # sep &

            # complex annotations
            annotations_oi = [self.user_classifications,
                              [self.get_recent_consensus_classification()],
                              [self.automatic_classification],
                              [self.clinvar],
                              self.heredicare_annotations,
                              self.consequences, 
                              self.assays, 
                              self.literature,
                              self.cancerhotspots_annotations
                            ]
            for annot in annotations_oi:
                if annot is not None:
                    if len(annot) > 0:
                        if annot[0] is not None:
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
            else:
                annot = self.get_most_recent_heredicare_consensus_classification()
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

    def get_string_repr(self):
        return '-'.join([self.chrom, str(self.start), str(self.end), self.sv_type])
    
    def get_custom_hgvs(self, hgvs_type):
        result = []
        for custom_hgvs in self.custom_hgvs:
            if custom_hgvs.hgvs_type == hgvs_type:
                result.append(custom_hgvs)
        return result

    def get_breakpoint_genes(self, how = "object"):
        result = []
        for overlapping_gene in self.overlapping_genes:
            gene_start = overlapping_gene[2]
            gene_end = overlapping_gene[3]
            if self.start in range(gene_start, gene_end) or self.end in range(gene_start, gene_end):
                result.append(overlapping_gene)
        if how == 'string':
            result = [x[1] for x in result]
        return result
    
    def get_genes(self, how = 'object'):
        if how == 'string':
            return [x[1] for x in self.overlapping_genes]
        if how == 'preferred':
            return functions.get_preferred_genes()
        return self.overlapping_genes
            

@dataclass
class import_request:
    id: int
    user: User
    requested_at: datetime.datetime
    status: str
    finished_at: datetime.datetime
    total_variants: int

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

@dataclass
class Annotation_type:
    id: int
    title: str
    display_title: str
    description: str
    value_type: str
    version: str
    version_date: str
    group_name: str
    is_transcript_specific: bool