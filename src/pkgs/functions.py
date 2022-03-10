import os


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
    file.write("# CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO\n")
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
    return info_headers, entries
