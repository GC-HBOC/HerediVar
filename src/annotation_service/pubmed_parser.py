from Bio import Entrez
import common.functions as functions
import re
import os

if os.environ.get('ENTREZ_MAIL') is None: # required for testing
    functions.read_dotenv()
Entrez.email = os.environ.get('ENTREZ_MAIL')

def fetch(pmids):
    pmids = pmids.replace('&', ',')
    handle = Entrez.efetch(db='pubmed', id=pmids, retmode='xml')
    records = Entrez.read(handle, validate = False)
    handle.close()
    result = []
    for record in records['PubmedArticle']: # PubmedBookArticle
        pubmed_essential_info = parse_record(record, 'MedlineCitation', 'Article', 'ArticleTitle', 'Journal', 'Title', 'ArticleDate')
        if '' not in pubmed_essential_info:
            result.append(pubmed_essential_info)
        else:
            functions.eprint("WARNING: skipping import of article: " + str(pubmed_essential_info) + " as there was missing data.")
    for record in records['PubmedBookArticle']:
        pubmed_essential_info = parse_record(record, 'BookDocument', 'Book', 'BookTitle', 'Publisher', 'PublisherName', 'PubDate', book = True)
        if '' not in pubmed_essential_info:
            result.append(pubmed_essential_info)
        else:
            functions.eprint("WARNING: skipping import of book: " + str(pubmed_essential_info) + " as there was missing data.")
    return result


def parse_record(rec, doc_section, article_section, title_section, journal_section, journal_title_section, date_section, book = False):
    pmid = rec[doc_section]['PMID']

    rec = rec[doc_section][article_section]
    
    year_section = rec[date_section]
    if not book:
        if len(year_section) >= 1:
            year_section = year_section[0]
    year = 0
    if 'Year' in year_section:
        year = year_section['Year']

    # the following tests if this is contained: year = rec['Journal']['JournalIssue']['PubDate']['Year']
    # this is a fallback if the date section is missing
    if year == 0:
        if 'Journal' in rec:
            curdict = rec['Journal']
            if 'JournalIssue' in curdict:
                curdict = curdict['JournalIssue']
                if 'PubDate' in curdict:
                    curdict = curdict['PubDate']
                    if 'Year' in curdict:
                        year = curdict['Year']
                    elif 'MedlineDate' in curdict:
                        res = re.search(r'[^\d](\d{4})[^\d]', ' ' + curdict['MedlineDate'] + ' ')
                        if res is not None:
                            year = res.group(1)


    article_title = rec.get(title_section, '')
    authors = []
    author_dict = rec.get('AuthorList', '')
    if author_dict != '':
        for author in author_dict:
            if book: # in bookarticle type pubmed entries the authors are wrapped within another list
                for a in author:
                    forename = a.get('ForeName', '')
                    lastname = a.get('LastName', '')
                    collective_name = a.get('CollectiveName', '')
                    fullname = functions.collect_info(forename, '', lastname, sep = ' ')
                    if fullname != '':
                        authors.append(fullname)
                    # the collective name is supposed to be a fallback in case there are no 'real' authors. 
                    # If the collective name is in its own author element and is preceded by real authors 
                    # which have a name it is however possible that you have both in the output!
                    if collective_name != '' and fullname == '' and len(authors) == 0: 
                        authors.append(collective_name)
            else:
                forename = author.get('ForeName', '')
                lastname = author.get('LastName', '')
                collective_name = author.get('CollectiveName', '')
                fullname = functions.collect_info(forename, '', lastname, sep = ' ')

                if fullname != '':
                    authors.append(fullname)
                if collective_name != '':
                    authors.append(collective_name)

    #journal = extract(extract(rec, journal_section), journal_title_section)
    journal = rec.get(journal_section, {}).get(journal_title_section, '')
    try:
        int(year)
    except:
        print(rec)

    return [int(pmid), str(article_title), ', '.join([str(x) for x in authors]), str(journal), int(year)]


