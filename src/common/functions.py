import os
import collections
import datetime
import re
import sys
import subprocess
import common.paths as paths
import tempfile

def basedir():
    return os.getcwd()


# converts one line from the variant table to a vcf record
def variant_to_vcf(chr, pos, ref, alt, path):
    #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
    chr_num = validate_chr(chr)
    if not chr_num:
        eprint("ERROR: not a valid chr number: " + str(chr) + " unable to write vcf.")
        return False
    if int(pos) < 0:
        eprint("ERROR: only non negative position numbers are allowed (" + str(pos) + ")")
        return False

    vcf_record = ["chr" + str(chr_num), str(pos), '.', str(ref), str(alt), '.', '.', '.']
    
    file = open(path, "w")
    write_vcf_header([], output_func = file.write, tail = "\n")
    file.write('\t'.join(vcf_record) + '\n')
    file.close()
    return True

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


def write_vcf_header(info_columns, output_func = print, tail = ""):
    output_func("##fileformat=VCFv4.2" + tail)
    output_func("##fileDate=" + datetime.datetime.today().strftime('%Y-%m-%d') + tail)
    output_func("##reference=GRCh38" + tail)
    for info_column in info_columns:
        output_func(info_column.strip() + tail)
    output_func("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO" + tail)


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
        
def remove_version_num(identifier, char = '.'):
    if char in identifier:
        return identifier[:identifier.find(char)]
    else:
        return identifier

def is_dna(strg, search=re.compile(r'[^ACGTacgt-]').search):
    return not bool(search(strg))

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def convert_none_infinite(x):
    if x is None:
        return -float('inf')
    else:
        return x

def execute_command(command, process_name):
    completed_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = completed_process.communicate()#[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    #vcf_errors = completed_process.communicate()[0].strip().decode("utf-8") # catch errors and warnings and convert to str
    std_err = std_err.strip().decode("utf-8")
    command_output = std_out.strip().decode("utf-8")
    err_msg = ""
    if completed_process.returncode != 0:
        err_msg = process_name + " runtime ERROR: " + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        err_msg = process_name + " runtime WARNING: " + std_err
    return completed_process.returncode, err_msg, command_output


def check_vcf(path):
    command = [paths.ngs_bits_path + "VcfCheck",
               "-in", path, "-lines", "0", "-ref", paths.ref_genome_path]
    returncode, err_msg, vcf_errors = execute_command(command, 'VcfCheck')
    return returncode, err_msg, vcf_errors


def left_align_vcf(path):
    command = [paths.ngs_bits_path + "VcfLeftNormalize",
               "-in", path, "-stream", "-ref", paths.ref_genome_path]
    returncode, err_msg, command_output = execute_command(command, 'VcfLeftNormalize')
    return returncode, err_msg, command_output


def hgvsc_to_vcf(hgvs):
    tmp_file_path = tempfile.gettempdir() + "/hgvs_to_vcf"

    tmp_file = open(tmp_file_path + ".tsv", "w")
    tmp_file.write("#reference	hgvs_c\n")
    reference, hgvs = split_hgvs(hgvs)
    tmp_file.write(reference + "\t" + hgvs + "\n")
    tmp_file.close()

    command = [paths.ngs_bits_path + "/HgvsToVcf", '-in', tmp_file_path + '.tsv', '-ref', paths.ref_genome_path, '-out', tmp_file_path + '.vcf']
    returncode, err_msg, command_output = execute_command(command, "HgvsToVcf")
    
    tmp_file = open(tmp_file_path + '.vcf', "r")
    for line in tmp_file: # this assumes a single-entry vcf
        if line.strip() == '' or line.startswith('#'):
            continue
        parts = line.split('\t')
        chr = parts[0]
        pos = parts[1]
        ref = parts[3]
        alt = parts[4]
    return chr, pos, ref, alt


# function for splitting hgvs in refrence transcript and variant
def split_hgvs(hgvs):
    reference = hgvs[:hgvs.find(':')]
    hgvs = hgvs[hgvs.find(':')+1:]
    return reference, hgvs


def find_between(s, prefix, postfix):
    res = re.search(prefix+r'(.*?)'+postfix, s)
    if res is not None:
        res = res.group(1)
    return res