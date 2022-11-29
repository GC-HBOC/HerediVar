import os
import collections
import datetime
import re
import sys
import subprocess
import common.paths as paths
import tempfile
import base64
import urllib.parse as urlparse
from urllib.parse import urlencode
from dotenv import load_dotenv


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
    chr = "chr" + str(chr_num)
    vcf_record = [chr, str(pos), '.', str(ref), str(alt), '.', '.', '.']
    
    file = open(path, "w")
    write_vcf_header(["##contig=<ID=%s>"%chr], output_func = file.write, tail = "\n")
    file.write('\t'.join(vcf_record) + '\n')
    file.close()
    return True

#def read_vcf_info(path):
#    file = open(path, "r")
#    entries = []
#    info_headers = []
#    for line in file:
#        if line.strip() == '':
#            continue
#        if line.startswith('##INFO'):
#            info_headers.append(line.strip())
#            continue
#        if not line.startswith('#'):
#            l = line.split('\t')[7]
#            entries.append(l.strip())
#    file.close()
#    return info_headers, entries


#Record = collections.namedtuple('Record', [
#    'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER'
#])


# doesnt collect FORMAT/INFO fields
#def read_vcf_variant(path):
#    all_records = []
#    for line in open(path, "r"):
#        if not line.startswith("#"):
#            prep_line = line.strip().split("\t")#[0:upper_bound]
#            rec = Record(prep_line[0], prep_line[1], prep_line[2], prep_line[3], prep_line[4], prep_line[5], prep_line[6])
#            all_records.append(rec)
#    return all_records
#    #variant = functions.read_vcf_variant(tmp_file_path)[0] # accessing only the first element of the returned list is save because we process only one variant at a time
#    #new_chr = variant.CHROM
#    #new_pos = variant.POS
#    #new_ref = variant.REF
#    #new_alt = variant.ALT


def write_vcf_header(info_columns, output_func = print, tail = "", reference_genome="GRCh38"):
    output_func("##fileformat=VCFv4.2" + tail)
    output_func("##fileDate=" + get_today() + tail)
    output_func("##reference=" + reference_genome + tail)
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
    values_to_join = []
    if old_info is not None and old_info != '':
        values_to_join.append(str(old_info))
    if new_value is not None and new_value != '':
        values_to_join.append(new_info_name + str(new_value))

    return sep.join(values_to_join)



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

def execute_command(command, process_name, use_prefix_error_log = True):
    completed_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = completed_process.communicate()#[1].strip().decode("utf-8") # catch errors and warnings and convert to str
    std_err = std_err.strip().decode("utf-8")
    command_output = std_out.strip().decode("utf-8")
    err_msg = ""
    if completed_process.returncode != 0:
        if use_prefix_error_log:
            err_msg = process_name + " runtime ERROR: "
        err_msg = err_msg + std_err + " Code: " + str(completed_process.returncode)
    elif len(std_err):
        if use_prefix_error_log:
            err_msg = process_name + " runtime WARNING: "
        err_msg = err_msg + std_err
    return completed_process.returncode, err_msg, command_output


def preprocess_variant(infile, do_liftover=False):
    final_returncode = 0
    err_msg = ""
    command_output = ""
    vcf_errors_pre = ""
    vcf_errors_post = ""

    if do_liftover:
        returncode, err_msg, vcf_errors_pre = check_vcf(infile, ref_genome="GRCh37")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
        returncode, err_msg, command_output = execute_command([paths.htslib_path + 'bgzip', '-f', '-k', infile], process_name="bgzip")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
        returncode, err_msg, command_output = perform_liftover(infile, infile + ".lifted")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
        returncode, err_msg, command_output = execute_command(["rm", infile + '.gz'], "rm")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
        returncode, err_msg, command_output = execute_command(["rm", infile], "rm")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
        returncode, err_msg, command_output = execute_command(["mv", infile + ".lifted", infile], "mv")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
    else:
        returncode, err_msg, vcf_errors_pre = check_vcf(infile, ref_genome="GRCh38")
        if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
    
    returncode, err_msg, command_output = left_align_vcf(infile, outfile= infile + ".leftnormalized", ref_genome="GRCh38")
    if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post

    returncode, err_msg, command_output = execute_command(["rm", infile], "rm")
    if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
    returncode, err_msg, command_output = execute_command(["mv", infile + ".leftnormalized", infile], "mv")
    if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post
    
    returncode, err_msg, vcf_errors_post = check_vcf(infile, ref_genome="GRCh38")
    if returncode != 0: return returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post

    return final_returncode, err_msg, command_output, vcf_errors_pre, vcf_errors_post


# infile has to be .gz
def perform_liftover(infile, outfile, from_genome="GRCh37", to_genome="GRCh38"):
    if from_genome == "GRCh37" and to_genome == "GRCh38":
        chainfile = paths.chainfile_path
    if to_genome == "GRCh38":
        genome_path = paths.ref_genome_path
    elif to_genome == "GRCh37":
        genome_path = paths.ref_genome_path_grch37

    returncode, err_msg, command_output = execute_command(['CrossMap.py', 'vcf', chainfile, infile, genome_path, outfile], process_name="CrossMap")
    return returncode, err_msg, command_output


def check_vcf(path, ref_genome = 'GRCh38'):
    genome_path = ''
    if ref_genome == 'GRCh37':
        genome_path = paths.ref_genome_path_grch37
    elif ref_genome == 'GRCh38': 
        genome_path = paths.ref_genome_path

    command = [paths.ngs_bits_path + "VcfCheck"]
    command.extend(["-in", path, "-lines", "0", "-ref", genome_path])
    returncode, err_msg, vcf_errors = execute_command(command, 'VcfCheck')

    return returncode, err_msg, vcf_errors

def left_align_vcf(infile, outfile, ref_genome = 'GRCh38'):
    genome_path = ''
    if ref_genome == 'GRCh37':
        genome_path = paths.ref_genome_path_grch37
    elif ref_genome == 'GRCh38': 
        genome_path = paths.ref_genome_path

    command = [paths.ngs_bits_path + "VcfLeftNormalize"]
    command.extend(["-in", infile, "-out", outfile, "-stream", "-ref", genome_path])
    returncode, err_msg, command_output = execute_command(command, 'VcfLeftNormalize')

    return returncode, err_msg, command_output


def hgvsc_to_vcf(hgvs):
    tmp_file_path = tempfile.gettempdir() + "/hgvs_to_vcf"
    tmp_file = open(tmp_file_path + ".tsv", "w")
    tmp_file.write("#reference	hgvs_c\n")
    reference, hgvs = split_hgvs(hgvs)
    tmp_file.write(reference + "\t" + hgvs + "\n")
    tmp_file.close()

    command = [paths.ngs_bits_path + "HgvsToVcf"]
    command.extend(['-in', tmp_file_path + '.tsv', '-ref', paths.ref_genome_path, '-out', tmp_file_path + '.vcf'])
    returncode, err_msg, command_output = execute_command(command, "HgvsToVcf", use_prefix_error_log=False)
    
    chr = None
    pos = None
    ref = None
    alt = None
    tmp_file = open(tmp_file_path + '.vcf', "r")
    for line in tmp_file: # this assumes a single-entry vcf
        if line.strip() == '' or line.startswith('#'):
            continue
        parts = line.split('\t')
        chr = parts[0]
        pos = parts[1]
        ref = parts[3]
        alt = parts[4]
    return chr, pos, ref, alt, err_msg

# function for splitting hgvs in refrence transcript and variant
def split_hgvs(hgvs):
    hgvs = hgvs.strip()
    double_point_pos = hgvs.find(':')
    if double_point_pos != -1:
        reference = hgvs[:double_point_pos].strip()
        hgvs = hgvs[double_point_pos+1:].strip()
        return reference, hgvs
    return None, hgvs
    


def find_between(s, prefix, postfix):
    res = re.search(prefix+r'(.*?)'+postfix, s)
    if res is not None:
        res = res.group(1)
    return res


# this function actually also maps ccds numbers!
def get_refseq_to_ensembl_transcript_dict(reverse = False):
    parsing_table = open(paths.parsing_refseq_ensembl, 'r')
    result = {}
    for line in parsing_table:
        if line.startswith('#') or line.strip() =='':
            continue

        parts = line.split('\t')
        if not reverse:
            value = parts[0].strip()
            key = parts[1].strip()
        else:
            key = parts[0].strip()
            value = parts[1].strip()
        if key in result:
            result[key] = collect_info(result[key], '', value, sep = ',')
        else:
            result[key] = value
    parsing_table.close()
    return result

def get_transcript_to_gene_dict():
    ensembl_to_refseq = get_refseq_to_ensembl_transcript_dict(reverse = True) # ccds included!
    gene_to_ensembl_file = open(paths.gene_to_ensembl_transcript_path, 'r')
    transcript_to_gene = {}
    for line in gene_to_ensembl_file:
        if line.startswith('#') or line.strip() =='':
            continue

        parts = line.split('\t')
        gene_symbol = parts[0].strip()
        ensembl = parts[1].strip()

        if ensembl in transcript_to_gene:
            eprint("skipping duplicated row: " + line.strip('\n'))
            continue

        transcript_to_gene[ensembl] = [gene_symbol]

        refseqs = ensembl_to_refseq.get(ensembl, None)
        # if there are no matching refseq or ccds numbers recorded skip the rest
        if refseqs is None:
            continue
        refseqs = refseqs.split(',')

        for alt_name in refseqs:
            if alt_name in transcript_to_gene:
                previous_gene = transcript_to_gene[alt_name]
                if gene_symbol not in previous_gene:
                    # if the previous gene symbol was a fusion gene replace it with the new gene symbol
                    # else keep as is
                    #if '-' in previous_gene:
                    #    transcript_to_gene[alt_name] = gene_symbol
                    #    continue
                    #if '-' not in previous_gene and '-' not in gene_symbol:
                    #eprint("multiple gene symbols for transcript " + alt_name + ': ' + gene_symbol + ' and ' + previous_gene)
                    transcript_to_gene[alt_name].append(gene_symbol)
                    #eprint("multiple gene symbols for transcript " + alt_name + ': ' + str(transcript_to_gene[alt_name]))
                    continue
            
            transcript_to_gene[alt_name] = [gene_symbol]
    gene_to_ensembl_file.close()

    transcript_to_gene = {k: curate_transcripts(k, v) for k, v in transcript_to_gene.items()}

    return transcript_to_gene

# this function removes all fusion genes from a list of genes while key is just for the error messages if there is more than one gene left
# or all genes were fusion genes!
def curate_transcripts(key, value):
    if len(value) > 1:
        value = [ x for x in value if "-" not in x ]
        if len(value) == 0:
            eprint("all genes were fusion genes and thus removed for transcript: " + key + ' and genes: ' + str(value))
        if len(value) > 1:
            eprint("multiple gene symbols for transcript " + key + ": " + str(value))
    return ','.join(value)


def complement(seq, missing_data = "NA"):
    seq = seq.upper()
    if seq == missing_data: # considered to be missing data (as used in the TP53 database)
        return ''
    seq = seq.replace('A', 't')
    seq = seq.replace('T', 'a')
    seq = seq.replace('C', 'g')
    seq = seq.replace('G', 'c')
    seq = seq.upper()
    return seq

def get_base64_encoding(path):
    with open(path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        return encoded_string

def buffer_to_base64(buffer):
    return base64.b64encode(buffer.getvalue())

# not used atm
#def base64_to_file(base64_string, path):
#    file_64_decode = decode_base64(base64_string) 
#    file_result = open(path, 'wb')
#    file_result.write(file_64_decode)
#    file_result.close()

def decode_base64(base64_string):
    return base64.b64decode(base64_string)

def encode_vcf(text):
    result = text.replace(' ', '_') \
                 .replace('\r', '') \
                 .replace('\n', '_') \
                 .replace('\t', '_' ) \
                 .replace(';', '%3B') \
                 .replace('$', '%24') \
                 .replace('#', '%23') \
                 .replace('+', '%2B') \
                 .replace('&', '%26') \
                 .replace('|', '%7C') \
                 .replace('~3B', ';') \
                 .replace('~24', '$') \
                 .replace('~23', '#') \
                 .replace('~2B', '+') \
                 .replace('~26', '&') \
                 .replace('~7C', '|')
    return result

def decode_vcf(text):
    result = text.replace('_', ' ') \
                 .replace('%3B', ';') \
                 .replace('%24', '$') \
                 .replace('%23', '#') \
                 .replace('%2B', '+') \
                 .replace('%26', '&') \
                 .replace('%7C', '|')
    return result

# new_params should be a dict
def add_args_to_url(url, new_params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(new_params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)


def get_today():
    return datetime.datetime.today().strftime('%Y-%m-%d')

def get_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def buffer_to_file_system(buffer, path):
    with open(path, 'w') as f:
        for line in buffer:
            f.write(line.decode('utf8'))


def is_snv(one_var):
    ref = one_var[3]
    alt = one_var[4]
    if len(ref) > 1 or len(alt) > 1:
        return False
    else:
        return True

def read_dotenv():
    basedir = os.path.abspath(os.path.dirname(__file__))


    webapp_env = os.environ.get('WEBAPP_ENV', None)


    if webapp_env is None:
        raise ValueError("No WEBAPP_ENV environment variable set.")


    dotenvfile = ".env"
    if webapp_env == "dev": #this is just for fast switching between configurations during development
        dotenvfile = ".env_dev"
    if webapp_env == "localtest":
        dotenvfile = ".env_localtest"
    
    load_dotenv(os.path.join(basedir, dotenvfile))