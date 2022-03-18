import os
import collections


def basedir():
    return os.getcwd()


# converts one line from the variant table to a vcf record
def variant_to_vcf(variant, path):
    # CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
    vcf_record = variant[1][3:] + "\t" + \
                str(variant[2]) + "\t" + \
                str(variant[0]) + "\t" + \
                variant[3] + "\t" + \
                variant[4] + "\t" + \
                "." + "\t" + \
                "." + "\t" + \
                "."
    file = open(path, "w")
    file.write("##fileformat=VCFv4.2\n")
    file.write("#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO\n")
    file.write(vcf_record)
    file.close()

def read_vcf_info(path):
    file = open(path, "r")
    entries = []
    info_headers = []
    for line in file:
        if line.startswith('##INFO'):
            info_headers.append(line.strip())
        if not line.startswith('#'):
            l = line.split('\t')[7]
            entries.append(l.strip())
    file.close()
    return info_headers, entries


Record = collections.namedtuple('Record', [
    'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER'
])


# doesnt collect FORMAT/INFO fields
def read_vcf_variant(path):
    all_records = []
    for line in open(path, "r"):
        if not line.startswith("#"):
            prep_line = line.strip().split("\t")#[0:upper_bound]
            rec = Record(prep_line[0], prep_line[1], prep_line[2], prep_line[3], prep_line[4], prep_line[5], prep_line[6])
            all_records.append(rec)
    return all_records
