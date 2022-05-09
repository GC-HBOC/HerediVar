# HerediCare API Endpoints

## Query SEQ-IDs

**Use case:** Query all SEQ-IDs (i.e. variant identifiers) from HerediCare.

| Parameter  | Definition                                              |
|------------|---------------------------------------------------------|
| Type:      | GET |
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/seq_id_list |
| Arguments: | n/a                                                     |
| Returns:   | [XML](seq_id_list_return.xsd) with all SEQ-IDs for which a VCF reprentation of the variant exists. |

**Questions:**
- Does each SEQ-ID identify one variant? If not, we need to curate them?!
- Can SEQ-IDs disapear/change? What do we do then?
- Format/Type of SEQ-IDs?


## GET: Query Variant

**Use case:** Get a variant in vcf format and its annotations corresponding to a SEQ-ID.

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Type:      | GET |
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/variant |
| Arguments: | **id**: *integer*, in query, The HerediCare Seq-ID                                         |
| Returns:   | [XML](variant_return.xsd) with: <ul><li>variant in VCF format: chr, pos, ref, alt, genomebuild</li><li>family history: the number of families showing this variant and the number of cases</li><li>previous classifications: center, classification, comment and boolean if it was the first classification (multiple possible)</li><li>likelihoods: segregation and tumorpathology likelihoods</li></ul>|

**Questions:**
- ..


## Upload Classification

**Use case:** Send task-force consensus classification for a variant back to HerediCare

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Type:      | POST |
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/upload-classification  |
| Arguments: | <ul><li>**id**: *integer*, in query, The HerediCare Seq-ID</li><li>**classification**: *XML*, in body, An [XML](upload_classification.xsd) file with class, date, pdf containing information about the classification (base-64 encoding)</li></ul> |
| Returns:   | n/a |

**Questions:**
- ..



## Create Variant

**Use case:** Create a new variant entry in HerediCare

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Type:      | POST |
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/upload-variant  |
| Arguments: | **variant**: *XML*, in body, An [XML](create_variant_upload.xsd) with chr, pos, ref, alt |
| Returns:   | [XML](create_variant_return.xsd) with new ID |

**Questions:**
- ..





<!-- 

## Likelihood ratio for segregation

**Use case:** Get the likelyhood for segregation for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/segregation   |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](segregation_return.xsd) with the segregation 'score'|

**Questions:**
- ..


## Likelihood ratio for tumorpathology

**Use case:** Get the likelyhood of tumorpathology for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/tumorpathology  |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](tumorpathology_return.xsd) with the tumorpathology score |

**Questions:**
- ..


## Family history


**Use case:** Get the family history for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/family_history |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](family_history_return.xsd) with the number of families showing this variant and the number of cases |

**Questions:**
- ..


## Classification


**Use case:** Get already existing classifications

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/classifications |
| Arguments: | seq_id=*[SEQ-ID]*                                         |
| Returns:   | [XML](classification_return.xsd) with center, classification, comment and if it was the first classification |

**Questions:**
- ..



## Get Likelihoods?

**Use case:** Get the likelihood for segregation and likelihood tumorpathology for a variant

| Parameter  | Definition                                                |
|------------|-----------------------------------------------------------|
| Url:       | https://*[host]*/HerediCareAPI/*[version]*/likelihoods   |
| Arguments: | id=*[int:ID]*                                         |
| Returns:   | [XML](likelihoods_return.xsd) with the segregation and tumorpathology likelihoods|

**Questions:**
- How long does it take to compute likelihoods? -> Merge with query variant endpoint if it is fast

-->

## Phenotypic data?

Anzahl Träger BC, OC, BCOC, nicht erkrankte + age at onset/diagnosis of disease + Ethnie + Geschlecht (Personenspezifische Daten höchstens temporär, speziell für TP53 [age at onset+Tumortyp+Familie])
? TP53 noch prüfen ob relevant > Gunnar

