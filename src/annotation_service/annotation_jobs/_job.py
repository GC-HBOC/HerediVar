import abc
import common.functions as functions

########## This class is an abstract class which needs to be implemented by
########## each annotation job used by the annotation service
class Job(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        pass

    # this function should return if we can execute the job
    @abc.abstractmethod
    def do_execution(self, job_config, queue: list) -> bool:
        pass

    # execute the job: this is the worker function
    @abc.abstractmethod
    def execute(self, conn):
       pass
    
    ## this is a template execute function:
    #def execute(self, conn):
    #    # update state
    #    self.status = "progress"
    #    self.print_executing()
    #
    #    # get arguments
    #    vcf_path = self.annotation_data.vcf_path
    #    annotated_path = vcf_path + ".ann.vcffromvcf"
    #    variant_id = self.annotation_data.variant.id
    #
    #    self.generated_paths.append(annotated_path)
    #
    #    # execute the annotation
    #
    #    # save to db
    #    info = self.get_info(annotated_path)
    #    self.save_to_db(info, variant_id, conn)
    #
    #    # update state
    #    self.status = "success"

    # requires that another job in the queue was already executed successfully
    def require_job(self, required_job, queue: list):
        for job in queue:
            if required_job.job_name == job.job_name:
                if job.status == "success" or job.status == "skipped":
                    return True
                break
        return False

    # takes a vcf file and extracts the info column [it is expected that the vcf file has only one variant]
    def get_info(self, vcf_path: str):
        info = ""
        with open(vcf_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                info = line.split('\t')[7]
        return info

    def print_executing(self):
        print("executing " + self.job_name + "...")

    def cleanup(self):
        for path in self.generated_paths:
            functions.rm(path)

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
