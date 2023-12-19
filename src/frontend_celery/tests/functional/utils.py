import re


def get_all_links(html_data):
    links = re.findall(r'href="(http.*?)"[ |>]', html_data)
    return links


def compare_vcf(reference_string: str, vcf_string: str):
    for line in reference_string.split('\n'):
        line = line.strip()
        if line == '':
            continue
        if line.startswith('#'): 
            if not line.startswith('##fileDate'): # skip the filedate header line because this one changes daily, but the test data is not updated daily
                if line not in vcf_string:
                    print(line)
                assert line in vcf_string # test that header line is there
            continue

        parts = line.split('\t')
        info = parts[7]

        assert info[0:7].join('\t') in vcf_string # test that variant is there

        for info_entry in info.split(';'):
            if 'consequences' in info_entry:
                for consequence in info_entry.strip('consequences=').split('&'):
                    assert consequence in vcf_string
            else:
                #if (info_entry not in vcf_string):
                #    print(info_entry)
                #    print(vcf_string)
                assert info_entry.strip() in vcf_string # test that info is there


def assert_flash_message(message, data):
    core_data = data[data.find("<!-- messages -->")+17:data.find("<!-- messages end -->")]
    core_data = re.sub(r"(\n *\n)+", "\n", core_data)
    try:
        assert message in core_data
    except AssertionError as error:
        print(core_data)
        raise error