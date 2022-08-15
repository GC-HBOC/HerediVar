import abc
import tempfile
import os
import common.functions as functions


# this is a static dictionary which all jobs have access to
# use this to collect data from multiple jobs or info-entries
# and insert them later to the db
saved_data = {}

########## This class is an abstract class which needs to be implemented by
########## each annotation job used by the annotation service
class Job(metaclass=abc.ABCMeta):


    @abc.abstractmethod
    def __init__(self):
        pass

    ## execute the job -> this should return the status code, stderr & stdout
    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def save_to_db(self, conn):
        pass



    def save_data(self, key, value):
        saved_data[key] = value
    
    def update_saved_data(self, key, value, operation = lambda x, y : x + y):
        saved_data[key] = operation(saved_data[key], value)
    
    def get_saved_data(self):
        return saved_data

    def print_executing(self):
        print("executing " + self.job_name + "...")

    def get_annotation_tempfile(self):
        res = tempfile.gettempdir() + "/_variant_annotated.vcf"
        return res
    
    def handle_result(self, inpath, code):
        self.update_output(inpath, self.get_annotation_tempfile(), code)
    
    def update_output(self, not_annotated_file_path, annotated_file_path, error_code):
        if error_code == 0: # execution worked and we want to keep the info
            os.replace(annotated_file_path, not_annotated_file_path)

    def insert_annotation(self, variant_id, info, info_name, annotation_type_id, conn, value_modifier_function = None):
        value = functions.find_between(info, info_name, '(;|$)')

        if value == '' or value is None:
            return

        if value_modifier_function is not None:
            value = value_modifier_function(value)

        conn.insert_variant_annotation(variant_id, annotation_type_id, value)