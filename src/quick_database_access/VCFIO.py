import collections
from datetime import date


Record = collections.namedtuple('Record', [
    'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'
])


# doesnt collect FORMAT info
def read_variants(path, info=False):
    all_records = []
    for line in open(path, "r"):
        if not line.startswith("#"):
            prep_line = line.strip().split("\t")#[0:upper_bound]
            rec = Record(prep_line[0], prep_line[1], prep_line[2], prep_line[3], prep_line[4], prep_line[5], prep_line[6], prep_line[7])
            all_records.append(rec)
    return all_records


# this does not write INFO / FORMAT information, FILTER is a problem as well
def write_variants(variants, dest):
    file = open(dest, "w")

    file.write("##fileformat=VCFv4.1" + "\n")
    file.write("##fileDate=" + str(date.today()) + "\n")
    file.write("##source=HerediVar" + "\n")
    file.write("##reference=GRCh38" + "\n")

    for line in variants:
        file.write(line.CHROM + "\t" +
                   line.POS + "\t" +
                   line.ID + "\t" +
                   line.REF + "\t" +
                   line.ALT + "\t" +
                   line.QUAL + "\t" +
                   line.FILTER)
        file.write("\n")


if __name__ == '__main__':
    variants = read_variants("./data/NA12878_03_export_20220308_ahsturm1.vcf")
    write_variants(variants, "./data/output_test.vcf")