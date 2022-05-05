# HerediCare API

## Query SEQ-IDs

**Use case:** Query all SEQ-IDs (i.e. variant identifiers) from HerediCare.

| Parameter  | Definition                                              |
|------------|---------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/seq_id_list |
| Arguments: | n/a                                                     |
| Returns:   | [XML](seq_id_list_return.xsd) with all SEQ-IDs for which a VCF reprentation of the variant exists. |

**Questions:**
- Does each SEQ-ID identify one variant? If not, we need to curate them?!
- Can SEQ-IDs disapear/change? What do we do then?
- Format of SEQ-IDs?


## Query variant

**Use case:** Get a variant in vcf format corresponding to a SEQ-ID.

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/*[seq_id]*/variant |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](variant_return.xsd) with chr, pos, ref, alt, genomebuild|

**Questions:**
- ..

## Likelihood ratio for segregation

**Use case:** Get the likelyhood for segregation for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/*[seq_id]*/segregation   |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](segregation_return.xsd) with the segregation 'score'|

**Questions:**
- ..


## Likelihood ratio for tumorpathology

**Use case:** Get the likelyhood of tumorpathology for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/*[seq_id]*/tumorpathology/  |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](tumorpathology_return.xsd) with the tumorpathology score |

**Questions:**
- ..


## Familyhistory


**Use case:** Get the family history for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/*[seq_id]*/family_history |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](family_history_return.xsd) with the number of families showing this variant and the number of cases |

**Questions:**
- ..


## Classification


**Use case:** Get already existing classifications

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/*[seq_id]*/classifications |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](classification_return.xsd) with center, classification, comment and if it was the first classification |

**Questions:**
- ..


## Phenotypic data?

Anzahl Träger BC, OC, BCOC, nicht erkrankte + age at onset/diagnosis of disease + Ethnie + Geschlecht (Personenspezifische Daten höchstens temporär, speziell für TP53 [age at onset+Tumortyp+Familie])
? TP53 noch prüfen ob relevant > Gunnar

