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
- Can SEQ-IDs disapear? What do we do then?


## Query variant

**Use case:** Get a variant corresponding to a SEQ-ID.

| Parameter  | Definition                                              |
|------------|---------------------------------------------------------|
| Url:       | https:://*[host]*/HerediCareAPI/*[version]*/seq_id_list |
| Arguments: | seq_id=*[SEQ-ID]*                                       |
| Returns:   | [XML](variant_return.xsd) with all SEQ-IDs for which a VCF reprentation of the variant exists. |

**Questions:**
- Does each SEQ-ID identify one variant? If not, we need to curate them?!
- Can SEQ-IDs disapear? What do we do then?

## Likelyhood ratio for segregation

## ...
