
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common.functions as functions
from common.xml_validator import xml_validator


class heredicare_interface:
    def __init__(self):
        self.base_url = "https://portal.img.med.uni-tuebingen.de/ahdoebm1/HerediCareAPI/v1/"
        self.variant_validator = xml_validator('/mnt/users/ahdoebm1/HerediVar/doc/api/variant.xsd')


    def get_heredicare_vid_list(self):
        execution_code = 0 # everything worked well
        list_validator = xml_validator('/mnt/users/ahdoebm1/HerediVar/doc/api/vid_list.xsd')
        v_id_list_request = requests.get(self.base_url + 'vid_list.php')
        #res = validator.validate('/mnt/users/ahdoebm1/HerediVar/src/tools/mock-api/vid_list.xml')
        v_id_list_xml = v_id_list_request.text
        is_valid = list_validator.validate(v_id_list_xml)

        if not is_valid:
            execution_code = 1 # fatal error: returned xml is not valid
            return execution_code, []
    
        vid_obj = list_validator.object_from_string(v_id_list_xml)
        vids_heredicare = []
        for vid in vid_obj.VId:
            vids_heredicare.append(vid.get('id'))
    
        return execution_code, vids_heredicare
    
    def get_variant(self, vid):
        execution_code = 0
        chr = ''
        pos = ''
        ref = ''
        alt = ''
        reference_genome_build = ''
        heredicare_variant = None

        variant_request = requests.get(self.base_url + 'variant.php?id=' + str(vid))
        variant_xml = variant_request.text

        # get orig variant
        heredicare_variant = self.variant_validator.object_from_string(variant_xml)
        chr = heredicare_variant.get('chr', '')
        pos = heredicare_variant.get('pos', '')
        ref = heredicare_variant.get('ref', '')
        alt = heredicare_variant.get('alt', '')
        reference_genome_build = heredicare_variant.get('genome_build', '')

        # errors
        if chr == '' or pos == '' or alt == '' or ref == '' or reference_genome_build == '':
            execution_code = 3
            return execution_code, chr, pos, ref, alt, reference_genome_build, heredicare_variant
        chr_num = functions.validate_chr(chr)
        if not chr_num:
            execution_code = 2
            return execution_code, chr, pos, ref, alt, reference_genome_build, heredicare_variant
        chr = 'chr' + chr_num
        is_valid_variant = self.variant_validator.validate(variant_xml)
        #print(variant_xml)
        if not is_valid_variant:
            execution_code = 1
            return execution_code, chr, pos, ref, alt, reference_genome_build, heredicare_variant

        # everything fine!
        return execution_code, chr, pos, ref, alt, reference_genome_build, heredicare_variant