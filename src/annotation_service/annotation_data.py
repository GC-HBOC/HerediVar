class Annotation_Data:
    def __init__(self, *args, **kwargs):
        self.job_config = kwargs['job_config']
        self.variant = kwargs['variant']
        self.vcf_path = kwargs['vcf_path']