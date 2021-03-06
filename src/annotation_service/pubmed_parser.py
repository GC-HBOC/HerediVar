from Bio import Entrez
import common.functions as functions

Entrez.email = 'marvin.doebel@med.uni-tuebingen.de'

def fetch(pmids):
    handle = Entrez.efetch(db='pubmed', id=pmids, retmode='xml')
    records = Entrez.read(handle)
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
    #print(rec)
    
    year_section = rec[date_section]
    if not book:
        if len(year_section) >= 1:
            year_section = year_section[0]
    year = ''
    if 'Year' in year_section:
        year = year_section['Year']

    # the following tests if this is contained: year = rec['Journal']['JournalIssue']['PubDate']['Year']
    # this is a fallback if the date section is missing
    if year == '':
        if 'Journal' in rec:
            curdict = rec['Journal']
            if 'JournalIssue' in curdict:
                curdict = curdict['JournalIssue']
                if 'PubDate' in curdict:
                    curdict = curdict['PubDate']
                    if 'Year' in curdict:
                        year = curdict['Year']


    article_title = extract(rec, title_section)
    authors = []
    author_dict = extract(rec, 'AuthorList')
    if author_dict != '':
        for author in author_dict:
            if book: # in bookarticle type pubmed entries the authors are wrapped within another list
                for a in author:
                    forename = extract(a, 'ForeName')
                    lastname = extract(a, 'LastName')
                    collective_name = extract(a, 'CollectiveName')
                    fullname = functions.collect_info(forename, '', lastname, sep = ' ')
                    if fullname != '':
                        authors.append(fullname)
                    # the collective name is supposed to be a fallback in case there are no 'real' authors. 
                    # If the collective name is in its own author element and is preceded by real authors 
                    # which have a name it is however possible that you have both in the output!
                    if collective_name != '' and fullname == '' and len(authors) == 0: 
                        authors.append(collective_name)
            else:
                forename = extract(author, 'ForeName')
                lastname = extract(author, 'LastName')
                collective_name = extract(author, 'CollectiveName')
                fullname = functions.collect_info(forename, '', lastname, sep = ' ')

                if fullname != '':
                    authors.append(fullname)
                if collective_name != '':
                    authors.append(collective_name)

    journal = extract(extract(rec, journal_section), journal_title_section)
    return [int(pmid), str(article_title), ', '.join([str(x) for x in authors]), str(journal), int(year)]

def extract(dictionary, key):  
    if key in dictionary:
        return dictionary[key]
    else:
        return ''
