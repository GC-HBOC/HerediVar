from .vep_job import vep_job
from .phylop_job import phylop_job
from .hexplorer_job import hexplorer_job
from .annotate_from_vcf_job import annotate_from_vcf_job
from .spliceai_job import spliceai_job
from .task_force_protein_domain_job import task_force_protein_domain_job
from .heredicare_job import heredicare_job
from .maxentscan_job import maxentscan_job
from .automatic_classification_job import automatic_classification_job
from .coldspots_job import coldspots_job
from .consequence_job import consequence_job
from .litvar2_job import litvar2_job
from .cancerhotspots_job import cancerhotspots_job

__all__ = ['vep_job', 
           'phylop_job', 
           'hexplorer_job', 
           'annotate_from_vcf_job', 
           'spliceai_job', 
           'task_force_protein_domain_job', 
           'heredicare_job', 
           'maxentscan_job', 
           'automatic_classification_job',
           'coldspots_job',
           'consequence_job',
           'litvar2_job',
           'cancerhotspots_job'
        ]