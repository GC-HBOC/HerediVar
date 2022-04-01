import os
import collections
import datetime


def basedir():
    return os.getcwd()


# converts one line from the variant table to a vcf record
def variant_to_vcf(variant, path):
    #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
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


def write_vcf_header(info_columns):
    print("##fileformat=VCFv4.2")
    print("##fileDate=" + datetime.datetime.today().strftime('%Y-%m-%d'))
    print("##reference=GRCh38")
    for info_column in info_columns:
        print(info_column.strip())
    print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")


def trim_chr(chr):
    chr = str(chr).upper()
    if chr.startswith('CHR'):
        return chr[3:]
    else:
        return chr


def validate_chr(chr, max = 22):
    chr = trim_chr(chr)

    if not chr in ['X', 'Y', 'M', 'MT'] and not chr in [str(i) for i in range(1,max+1)]:
        return False
    if chr == "M":
        return 'MT'
    else:
        return chr

def collect_info(old_info, new_info_name, new_value, sep = ';'):
    new_value = str(new_value)
    if old_info != '':
        if new_value == '':
            return old_info
        else:
            return old_info + sep + new_info_name + new_value
    else:
        if new_value == '':
            return old_info
        else:
            return new_info_name + new_value

def trim_hgnc(hgnc_id):
    hgnc_id = hgnc_id.upper()
    if hgnc_id.startswith('HGNC:'):
        return hgnc_id[5:]
    else:
        return hgnc_id
        
def remove_version_num(identifier, char = ':'):
    if char in identifier:
        return identifier[identifier.find(char)+1:]
    else:
        return identifier