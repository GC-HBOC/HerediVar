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
import json
import uuid
from functools import cmp_to_key
import pathlib

def prettyprint_json(json_obj, func = print):
    pretty_json = json.dumps(json_obj, indent=2)
    if func is not None:
        func(pretty_json)
    else:
        return pretty_json
    

def basedir():
    return os.getcwd()

def load_webapp_env():
    webapp_env = os.environ.get('WEBAPP_ENV', None)
    if webapp_env is None:
        raise ValueError("No WEBAPP_ENV environment variable set.")
    return webapp_env

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

def cnv_to_bed(chrom, start, end, path):
    with open(path, "w") as file:
        line = '\t'.join([chrom, str(start), str(end)])
        file.write(line + '\n')
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


def get_refseq_chom_to_chrnum():
    # taken from: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_assembly_report.txt
    refseq_dict = {"NC_000001.11": "chr1", "NC_000002.12": "chr2", "NC_000003.12": "chr3", "NC_000004.12": "chr4", "NC_000005.10": "chr5",
               "NC_000006.12": "chr6", "NC_000007.14": "chr7", "NC_000008.11": "chr8", "NC_000009.12": "chr9", "NC_000010.11": "chr10",
               "NC_000011.10": "chr11", "NC_000012.12": "chr12", "NC_000013.11": "chr13", "NC_000014.9": "chr14", "NC_000015.10": "chr15",
               "NC_000016.10": "chr16", "NC_000017.11": "chr17", "NC_000018.10": "chr18", "NC_000019.10": "chr19", "NC_000020.11": "chr20",
               "NC_000021.9": "chr21", "NC_000022.11": "chr22", "NC_000023.11": "chrX", "NC_000024.10": "chrY", "NC_012920.1": "chrMT"}
    return refseq_dict

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

    if do_liftover:
        returncode, err_msg, vcf_errors_pre = check_vcf(infile, ref_genome="GRCh37")
        if returncode != 0: return returncode, err_msg + " " + vcf_errors_pre, command_output
        returncode, err_msg, command_output = bgzip(infile)
        if returncode != 0: return returncode, err_msg, command_output
        returncode, err_msg, command_output = perform_liftover(infile, infile + ".lifted")
        if returncode != 0: return returncode, err_msg, command_output
        returncode, err_msg, command_output = execute_command(["rm", infile + '.gz'], "rm")
        if returncode != 0: return returncode, err_msg, command_output
        returncode, err_msg, command_output = execute_command(["rm", infile], "rm")
        if returncode != 0: return returncode, err_msg, command_output
        returncode, err_msg, command_output = execute_command(["mv", infile + ".lifted", infile], "mv")
        if returncode != 0: return returncode, err_msg, command_output
    else:
        returncode, err_msg, vcf_errors_pre = check_vcf(infile, ref_genome="GRCh38")
        if vcf_errors_pre != '': return 1, err_msg + " " + vcf_errors_pre, command_output
        if returncode != 0: return returncode, err_msg, command_output
    
    returncode, err_msg, command_output = left_align_vcf(infile, outfile= infile + ".leftnormalized", ref_genome="GRCh38")
    if returncode != 0: return returncode, err_msg, command_output

    returncode, err_msg, command_output = execute_command(["rm", infile], "rm")
    if returncode != 0: return returncode, err_msg, command_output
    returncode, err_msg, command_output = execute_command(["mv", infile + ".leftnormalized", infile], "mv")
    if returncode != 0: return returncode, err_msg, command_output
    
    returncode, err_msg, vcf_errors_post = check_vcf(infile, ref_genome="GRCh38")
    if vcf_errors_post != '': return 1, err_msg + " " + vcf_errors_post, command_output
    if returncode != 0: return returncode, err_msg, command_output

    return final_returncode, err_msg, command_output

def bgzip(path):
    returncode, err_msg, command_output = execute_command([os.path.join(paths.htslib_path, 'bgzip'), '-f', '-k', path], process_name="bgzip")
    return returncode, err_msg, command_output

def curate_chromosome(chrom):
    if chrom is None:
        return None, False
    is_valid = True
    chr_num = validate_chr(chrom)

    if not chr_num:
        is_valid = False
        return chrom, is_valid
    
    return 'chr' + chr_num, is_valid


def curate_position(pos):
    is_valid = True
    if pos is None or pos.strip() == '':
        is_valid = False
        return None, is_valid
    pos = str(pos).replace(',', '').replace('.', '').strip()
    allowed = "0123456789"
    is_valid = all(c in allowed for c in pos)
    if is_valid:
        return int(pos), is_valid
    else:
        return pos, is_valid

def curate_sequence(seq, allowed = "ACGT-"):
    if seq is None:
        return None, False
    if len(seq) > 1000:
        return seq, False
    seq = seq.strip().upper()
    is_valid = True
    if not all(c in allowed for c in seq):
        is_valid = False
    if len(seq) == 0:
        is_valid = False
    return seq, is_valid

def filename_allowed(filename, allowed_extensions = {'vcf', 'txt'}):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


# infile has to be .gz
def perform_liftover(infile, outfile, from_genome="GRCh37", to_genome="GRCh38", infile_format = "vcf"):
    if from_genome == "GRCh37" and to_genome == "GRCh38":
        chainfile = paths.chainfile_path
    if to_genome == "GRCh38":
        genome_path = paths.ref_genome_path
    elif to_genome == "GRCh37":
        genome_path = paths.ref_genome_path_grch37

    command = ['CrossMap.py', infile_format, chainfile, infile]
    if infile_format == 'vcf':
        command.append(genome_path)
    command.append(outfile)
    returncode, err_msg, command_output = execute_command(command, process_name="CrossMap")
    return returncode, err_msg, command_output


def check_vcf(path, ref_genome = 'GRCh38'):
    genome_path = ''
    if ref_genome == 'GRCh37':
        genome_path = paths.ref_genome_path_grch37
    elif ref_genome == 'GRCh38': 
        genome_path = paths.ref_genome_path

    command = [os.path.join(paths.ngs_bits_path, "VcfCheck")]
    command.extend(["-in", path, "-lines", "0", "-ref", genome_path])
    returncode, err_msg, vcf_errors = execute_command(command, 'VcfCheck')

    return returncode, err_msg, vcf_errors

def left_align_vcf(infile, outfile, ref_genome = 'GRCh38'):
    genome_path = ''
    if ref_genome == 'GRCh37':
        genome_path = paths.ref_genome_path_grch37
    elif ref_genome == 'GRCh38': 
        genome_path = paths.ref_genome_path

    command = [os.path.join(paths.ngs_bits_path, "VcfLeftNormalize")]
    command.extend(["-in", infile, "-out", outfile, "-stream", "-ref", genome_path])
    returncode, err_msg, command_output = execute_command(command, 'VcfLeftNormalize')

    return returncode, err_msg, command_output

## DEPRECATED
#def hgvsc_to_vcf(hgvs, reference = None):
#    #tmp_file_path = tempfile.gettempdir() + "/hgvs_to_vcf"
#    tmp_file_path = get_random_temp_file("_hgvs2vcf")
#    tmp_file = open(tmp_file_path + ".tsv", "w")
#    tmp_file.write("#reference	hgvs_c\n")
#    if reference is None:
#        reference, hgvs = split_hgvs(hgvs)
#    tmp_file.write(reference + "\t" + hgvs + "\n")
#    tmp_file.close()
#
#    command = [os.path.join(paths.ngs_bits_path, "HgvsToVcf")]
#    command.extend(['-in', tmp_file_path + '.tsv', '-ref', paths.ref_genome_path, '-out', tmp_file_path + '.vcf'])
#    returncode, err_msg, command_output = execute_command(command, "HgvsToVcf", use_prefix_error_log=False)
#    
#    chr = None
#    pos = None
#    ref = None
#    alt = None
#    tmp_file = open(tmp_file_path + '.vcf', "r")
#    for line in tmp_file: # this assumes a single-entry vcf
#        if line.strip() == '' or line.startswith('#'):
#            continue
#        parts = line.split('\t')
#        chr = parts[0]
#        pos = parts[1]
#        ref = parts[3]
#        alt = parts[4]
#    
#
#    rm(tmp_file_path + ".tsv")
#    rm(tmp_file_path + ".vcf")
#    return chr, pos, ref, alt, err_msg


def hgvsc_to_vcf(hgvs_strings, references = None):
    #tmp_file_path = tempfile.gettempdir() + "/hgvs_to_vcf"
    tmp_file_path = get_random_temp_file("_hgvs2vcf")
    tmp_file = open(tmp_file_path + ".tsv", "w")
    tmp_file.write("#reference	hgvs_c\n")
    if references is None:
        references = []
        if isinstance(hgvs_strings, str):
            hgvs_strings = [hgvs_strings]
        for hgvs in hgvs_strings:
            reference, hgvs = split_hgvs(hgvs)
            references.append(reference)
            tmp_file.write(reference + "\t" + hgvs + "\n")
    else:
        for hgvs, reference in zip(hgvs_strings, references):
            tmp_file.write(reference + "\t" + hgvs + "\n")
    tmp_file.close()

    command = [os.path.join(paths.ngs_bits_path, "HgvsToVcf")]
    command.extend(['-in', tmp_file_path + '.tsv', '-ref', paths.ref_genome_path, '-out', tmp_file_path + '.vcf'])
    returncode, err_msg, command_output = execute_command(command, "HgvsToVcf", use_prefix_error_log=False)
    
    chr = None
    pos = None
    ref = None
    alt = None
    first_iter = True
    tmp_file = open(tmp_file_path + '.vcf', "r")
    for line in tmp_file: # this assumes a single-entry vcf
        if line.strip() == '' or line.startswith('#'):
            continue
        parts = line.split('\t')

        #print(parts)

        if first_iter:
            chr = parts[0]
            pos = parts[1]
            ref = parts[3]
            alt = parts[4]
            first_iter = False
        else:
            if chr != parts[0] or pos != parts[1] or ref != parts[3] or alt != parts[4]: # check that all are equal
                tmp_file.close()
                rm(tmp_file_path + ".tsv")
                rm(tmp_file_path + ".vcf")
                return None, None, None, None, "HGVSc recovered vcf-style variant among transcripts is unequal: " + str(references)
    
    tmp_file.close()
    rm(tmp_file_path + ".tsv")
    rm(tmp_file_path + ".vcf")
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
    result = decode_html(text)
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
                 .replace('=', '%1Y') \
                 .replace('~3B', ';') \
                 .replace('~24', '$') \
                 .replace('~23', '#') \
                 .replace('~2B', '+') \
                 .replace('~26', '&') \
                 .replace('~7C', '|') \
                 .replace('~1Y', '=')
    return result

def decode_vcf(text):
    result = text.replace('_', ' ') \
                 .replace('%3B', ';') \
                 .replace('%24', '$') \
                 .replace('%23', '#') \
                 .replace('%2B', '+') \
                 .replace('%26', '&') \
                 .replace('%7C', '|') \
                 .replace('%1Y', '=')
    return result

def encode_html(text): # this escapes special characters for the use in html text
    result = text.replace('>', '&gt;') \
                 .replace('<', '&lt;')
    return result

def decode_html(text):
    result = text.replace('&gt;', '>') \
                 .replace('&lt;', '<')
    return result


# a helper function for the generation of vcf lines
def process_multiple(list_of_objects, sep = '~26', do_prefix = True) -> str:
    infos = [] # collect info vcfs in here
    #print(list_of_objects)
    for obj in list_of_objects:
        new_info = obj.to_vcf(prefix = do_prefix)
        infos.append(new_info)
        do_prefix = False
    new_info = sep.join(infos)
    return new_info

def list_of_objects_to_dict(list_of_objects, key_func = lambda a : a, val_func = lambda a : a):
    result = {}
    for object in list_of_objects:
        key = key_func(object)
        value = val_func(object)
        result[key] = value
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

def reformat_date(date_str, input_pattern, output_pattern):
    datetime_obj = datetime.datetime.strptime(date_str, input_pattern)
    return datetime_obj.strftime(output_pattern)

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
    webapp_env = os.environ.get('WEBAPP_ENV', None)
    if webapp_env is None:
        raise ValueError("No WEBAPP_ENV environment variable set.")

    dotenv_filename = ".env_" + webapp_env
    dotenv_path = os.path.join(paths.workdir, dotenv_filename)

    if not os.path.exists(dotenv_path):
        raise IOError("The .env file is missing: " + dotenv_path)
    
    load_dotenv(dotenv_path)

def enquote(string):
    string = str(string).strip("'") # remove quotes if the input string is already quoted!
    return "'" + string + "'"

def enbrace(string):
    #string = str(string).strip("(").strip(")")
    string = "(" + string + ")"
    return string

def enpercent(string):
    string = str(string).strip('%')
    return '%' + string + '%'


def get_random_temp_file(fileending, filename_ext = ""):
    filename = collect_info(str(uuid.uuid4()), "", filename_ext, sep = '_')
    return os.path.join(tempfile.gettempdir(), filename + "." + str(fileending.strip('.'))).strip('.')

def rm(path):
    if os.path.exists(path): 
        os.remove(path)

def remove_oldest_file(folder, maxfiles=10):
    if os.path.exists(folder):
        list_of_files = os.listdir(folder)
        full_paths = [os.path.abspath(os.path.join(folder, x)) for x in list_of_files if not os.path.basename(x).startswith('.')]

        if len(list_of_files) >= maxfiles:
            oldest_file = min(full_paths, key=os.path.getctime)
            os.remove(oldest_file)


def mkdir_recursive(dirpath):
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)

def str2datetime(datetime_str, fmt):
    if datetime_str is None:
        return None
    else:
        return datetime.datetime.strptime(datetime_str, fmt)



def order_classes( classes):
    keyfunc = cmp_to_key(mycmp = sort_classes)
    classes = [str(x) for x in classes]
    classes.sort(key = keyfunc) # sort by preferred transcript
    return classes
 
def sort_classes(a, b):
    # sort by ensembl/refseq
    class_sequence = ['1', '2', '3-', '3', '3+', '4M', '4', '5', 'R']

    a_importance = class_sequence.index(a)
    b_importance = class_sequence.index(b)

    if a_importance > b_importance:
        return 1
    elif a_importance < b_importance:
        return -1
    return 0

def reverse_seq(seq):
    seq = seq.upper().replace('A', 't').replace('T', 'a').replace('G', 'c').replace('C', 'g')
    return seq.upper()


# keys: transcript names, values: something to be sorted by transcript
# returns sorted list of values by transcript
def sort_transcript_dict(input_dict):
    transcript_names = input_dict.keys()
    transcript_names_sorted = sort_transcripts(transcript_names)

    result = []
    for transcript_name in transcript_names_sorted:
        result.append(input_dict[transcript_name])
    return transcript_names_sorted, result


# this function sorts a list of transcript names (ENSTxxx strings)
def sort_transcripts(transcript_names):
    from common.db_IO import Connection
    conn = Connection()
    transcripts = conn.get_transcripts_from_names(transcript_names, remove_unknown = True)
    conn.close()
    transcripts_sorted = order_transcripts(transcripts)
    return [transcript.name for transcript in transcripts_sorted]


def order_transcripts(transcripts):
    keyfunc = cmp_to_key(mycmp = sort_transcripts_worker)
    transcripts.sort(key = keyfunc) # sort by preferred transcript
    return transcripts


def sort_transcripts_worker(a, b):
    # sort by ensembl/refseq
    if a.source == 'ensembl' and b.source == 'refseq':
        return -1
    elif a.source == 'refseq' and b.source == 'ensembl':
        return 1
    elif a.source == b.source:
        # sort by mane select
        if a.is_mane_select is None or b.is_mane_select is None:
            return 1
        elif a.is_mane_select and not b.is_mane_select:
            return -1
        elif not a.is_mane_select and b.is_mane_select:
            return 1
        elif a.is_mane_select == b.is_mane_select:
            # sort by biotype
            if a.biotype == 'protein coding' and b.biotype != 'protein coding':
                return -1
            elif a.biotype != 'protein coding' and b.biotype == 'protein coding':
                return 1
            elif (a.biotype != 'protein coding' and b.biotype != 'protein coding') or (a.biotype == 'protein coding' and b.biotype == 'protein coding'):
                # sort by length
                if a.length is None and b.length is not None:
                    return 1
                elif a.length is not None and b.length is None:
                    return -1
                if a.length > b.length:
                    return -1
                elif a.length < b.length:
                    return 1
                else:
                    return 0


# one to many mapping
def num2heredicare(classification, single_value = False):
    if classification is None:
        return "-"
    if single_value:
        mapping = {
            "5": "15",
            "3": "13",
            "1": "11",
            "2": "12",
            "3-": "32",
            "3+": "34",
            "4": "14",
            "-": "21",
            "4M": "14"
        }
    else:
        mapping = {
            "5": ["1", "15"],
            "3": ["2", "13"],
            "1": ["3", "11"],
            "2": ["12"],
            "3-": ["32"],
            "3+": ["34"],
            "4": ["14"],
            "-": ["20", "21", "4", "-1"],
            "4M": ["14"]
    }

    return mapping[str(classification)]


def extend_dict(dictionary, key, new_value):
    if key in dictionary:
        dictionary[key].append(new_value)
    else:
        dictionary[key] = [new_value]
    return dictionary

# format: chr:start-stop
def get_sequence(chrom: str, start: int, end: int):
    # chrom, start and end is the region of interest
    # The resulting sequence will be of length size with the region of interest in the middle
    if not chrom.startswith('chr'):
        chrom = 'chr' + str(chrom)

    region = chrom + ':' + str(start) + '-' + str(end)

    command = [paths.samtools_path, 'faidx', paths.ref_genome_path, region]
    returncode, stderr, stdout = execute_command(command, process_name='samtools')

    if returncode != 0:
        raise ValueError("There was an error during sequence retrieval using samtools:" + stderr)

    # stdout contains the sequences
    sequence, region = extract_sequence(stdout)
    return sequence, region

# fasta_str should only contain a single fasta entry
def extract_sequence(fasta_str):
    lines = fasta_str.split('\n')
    sequence = ""
    region = ""
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if line.startswith('>'):
            region = line.strip('>')
        else:
            sequence += line
    return sequence, region

def get_sv_variant_sequence(chrom, start, end, sv_type):
    start = int(start)
    end = int(end)
    ref = ""
    alt = ""
    pos = start

    if sv_type == 'DEL':
        sequence, region = get_sequence(chrom, start - 1, end) # subtract one because we need one reference base

        if len(sequence) < 1001:
            ref = sequence
            alt = sequence[0]
            pos = start - 1
        else:
            ref = sequence[1]
            alt = "<DEL>"
    
    elif sv_type == 'DUP' or sv_type == 'INV':
        sequence, region = get_sequence(chrom, start, end) ## never put the full sequence

        ref = sequence[0]
        alt = "<" + sv_type +">"

    return ref, alt, pos




def get_preferred_genes():
    return set(["ATM", "BARD1", "BRCA1", "BRCA2", "BRIP1", "CDH1", "CHEK2", "PALB2", "PTEN", "RAD51C", "RAD51D", "STK11", "TP53"])


def none_to_empty_list(obj):
    if obj is None:
        return []
    return obj

def none2default(obj, default):
    if obj is None:
        return default
    return obj

def percent_to_decimal(input) -> float:
    if input is None:
        return None
    input = float(input)
    input = input / 100
    return input