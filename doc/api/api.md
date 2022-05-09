# HerediCare API Endpoints

## Query SEQ-IDs

**Use case:** Query all SEQ-IDs (i.e. variant identifiers) from HerediCare.

| Parameter  | Definition                                              |
|------------|---------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/seq_id_list  |
| Arguments: | n/a                                                     |
| Returns:   | [XML](seq_id_list.xsd) with all SEQ-IDs for which a VCF reprentation of the variant exists. |

**Questions:**
- Format of SEQ-IDs? Integer
- SEQ-IDs can be deleted. Delete them in HerediVar as well, unless there is a classification for it.
- Does each SEQ-ID identify one variant? We should check for duplicates!


## Query variant data and annotations

**Use case:** Get a variant in VCF-style and annotations for HerediCare.

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/variant        |
| Arguments: | **id** (*integer/GET*): the HerediCare Seq-ID             |
| Returns:   | [XML](variant.xsd) with: <ul><li>variant in VCF-like representation: chr, pos, ref, alt, genomebuild</li><li>family history: the number of families showing this variant and the number of cases</li><li>previous classifications: center, classification, comment and boolean if it was the first classification (multiple possible)</li></ul>|


## Upload Classification

**Use case:** Send consensus classification of VUS Task-Force back to HerediCare

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/upload-classification  |
| Arguments: | <ul><li>**id** (*integer/GET*): The HerediCare Seq-ID</li><li>**classification** (*XML/POST)*: An [XML](upload_classification.xsd) file with class, date, pdf containing information about the classification (base-64 encoding)</li></ul> |
| Returns:   | n/a (only return code 200, 400, ...)  |


## Create Variant

**Use case:** Create a new variant entry in HerediCare for variants that were created in HerediVar

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/upload-variant |
| Arguments: | <ul><li>**chr** (*enum/GET)*: chr, chr2, ..., chrX, chrY, chrMT</li><li>**pos** (*int/GET*): chromosomal position</li><li>**ref** (*string/GET*): reference sequence</li><li>**alt** (*string/GET*): alternative/observed sequence</li></ul>|
| Returns:   | [XML](create_variant.xsd) with new ID |


## Likelyhoods?

segregation and tumorpathology likelihoods

## Phenotypic data?

Anzahl Träger BC, OC, BCOC, nicht erkrankte + age at onset/diagnosis of disease + Ethnie + Geschlecht (Personenspezifische Daten höchstens temporär, speziell für TP53 [age at onset+Tumortyp+Familie])
? TP53 noch prüfen ob relevant > Gunnar
