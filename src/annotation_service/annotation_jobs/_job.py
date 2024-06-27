import abc
import tempfile
import os
import common.functions as functions


# this is a static dictionary which all jobs have access to
# use this to collect data from multiple jobs or info-entries
# and insert them later to the db
#saved_data = {}

########## This class is an abstract class which needs to be implemented by
########## each annotation job used by the annotation service
class Job(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        pass

    ## execute the job -> this should return the status code, stderr & stdout
    @abc.abstractmethod
    def execute(self, conn):
       pass

    @abc.abstractmethod
    def do_execution(self, job_config, queue: list):
        pass

    def require_job(self, required_job, queue: list):
        for job in queue:
            if required_job.job_name == job.job_name:
                if job.status == "success" or job.status == "skipped":
                    return True
                break
        return False

    def get_info(self, vcf_path: str):
        info = ""
        with open(vcf_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                info = line.split('\t')[7]
        return info



    #def save_data(self, key, value):
    #    saved_data[key] = value
    
    #def update_saved_data(self, key, value, operation = lambda x, y : x + y):
    #    saved_data[key] = operation(saved_data[key], value)
    
    #def get_saved_data(self):
    #    return saved_data

    def print_executing(self):
        print("executing " + self.job_name + "...")

    def cleanup(self):
        for path in self.generated_paths:
            functions.rm(path)
    
    #def handle_result(self, inpath, annotated_inpath, code):
    #    self.update_output(inpath, annotated_inpath, code)
    #
    #def update_output(self, not_annotated_file_path, annotated_file_path, error_code):
    #    if error_code == 0: # execution worked and we want to keep the info
    #        returncode, err, out = functions.execute_command(["mv", annotated_file_path, not_annotated_file_path], "mv")
    #        #os.replace(annotated_file_path, not_annotated_file_path)

    def insert_annotation(self, variant_id, info, info_name, annotation_type_id, conn, value_modifier_function = None):
        value = functions.find_between(info, info_name, '(;|$)')

        if value == '' or value is None:
            return

        if value_modifier_function is not None:
            value = value_modifier_function(value)

        conn.insert_variant_annotation(variant_id, annotation_type_id, value)

    def insert_external_id(self, variant_id, info, info_name, annotation_type_id, conn, value_modifier_function = None):
        value = functions.find_between(info, info_name, '(;|$)')

        if value == '' or value is None:
            return

        if value_modifier_function is not None:
            value = value_modifier_function(value)

        conn.insert_external_variant_id(variant_id = variant_id, annotation_type_id = annotation_type_id, external_id = value)

    def insert_multiple_ids(self, variant_id, info, info_name, annotation_type_id, conn, sep, value_modifier_function = None):
        value = functions.find_between(info, info_name, '(;|$)')

        if value == '' or value is None:
            return
        
        if value_modifier_function is not None:
            value = value_modifier_function(value)

        id_list = value.split(sep)

        for external_id in id_list:
            conn.insert_external_variant_id(variant_id, external_id, annotation_type_id)
