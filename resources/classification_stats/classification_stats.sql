-- get errors of classifications
SELECT a1.variant_id, 
	   (SELECT chr FROM variant WHERE a1.variant_id = variant.id) as chrom, 
       (SELECT pos FROM variant WHERE a1.variant_id = variant.id) as pos, 
       (SELECT ref FROM variant WHERE a1.variant_id = variant.id) as ref, 
       (SELECT alt FROM variant WHERE a1.variant_id = variant.id) as alt, 
       a1.status, 
       a1.error_message
    FROM annotation_queue a1 LEFT JOIN annotation_queue a2
        ON (a1.variant_id = a2.variant_id AND a1.requested < a2.requested)
WHERE a2.id IS NULL and a1.status = "error" and a1.error_message LIKE "%Annotation service runtime error:%"


-- stats about herediclassify
SELECT COUNT(id) FROM automatic_classification

select
    count(*) RecordsPerGroup,
    name,is_selected,strength
from automatic_classification_criteria_applied
group by name,is_selected,strength


select
    count(*) RecordsPerGroup,
    classification_splicing
from automatic_classification
group by classification_splicing

select
    count(*) RecordsPerGroup,
    classification_protein
from automatic_classification
group by classification_protein




-- stats about consensus
SELECT COUNT(id) FROM consensus_classification WHERE is_recent= 1

SELECT 
    count(*) RecordsPerGroup,
    (SELECT name FROM classification_criterium WHERE classification_criterium.id = consensus_classification_criteria_applied.classification_criterium_id) name,
    state,
    (SELECT name FROM classification_criterium_strength WHERE classification_criterium_strength.id = consensus_classification_criteria_applied.criterium_strength_id) strength
FROM consensus_classification_criteria_applied WHERE consensus_classification_id in (SELECT id FROM consensus_classification WHERE is_recent = 1)
group by name,state,strength

select
    count(*) RecordsPerGroup,
    classification
from consensus_classification WHERE is_recent = 1
group by classification




-- stats about heredicare
SELECT COUNT(id) FROM variant_heredicare_annotation WHERE consensus_class is not null

select
    count(*) RecordsPerGroup,
    consensus_class
from variant_heredicare_annotation
group by consensus_class





-- GEGENÜBERSTELLUNG
-- herediclassify splicing vs consensus
select
    count(*) RecordsPerGroup,
    consensus_class,
    splicing_class
from 
(SELECT 
	variant_id, 
	classification as consensus_class, 
	(SELECT classification_splicing FROM automatic_classification WHERE automatic_classification.variant_id = consensus_classification.variant_id) as splicing_class 
FROM consensus_classification WHERE is_recent = 1
)s
group by consensus_class,splicing_class

-- herediclassify protein vs consensus
select
    count(*) RecordsPerGroup,
    consensus_class,
    protein_class
from 
(SELECT 
	variant_id, 
	classification as consensus_class, 
	(SELECT classification_protein FROM automatic_classification WHERE automatic_classification.variant_id = consensus_classification.variant_id) as protein_class 
FROM consensus_classification WHERE is_recent = 1
)s
group by consensus_class,protein_class


-- herediclassify splicing vs heredicare
select
    count(*) RecordsPerGroup,
    consensus_class,
    splicing_class
from 
(SELECT 
	variant_id, 
	consensus_class, 
	(SELECT classification_splicing FROM automatic_classification WHERE automatic_classification.variant_id = variant_heredicare_annotation.variant_id) as splicing_class 
FROM variant_heredicare_annotation
)s
group by consensus_class,splicing_class


-- herediclassify protein vs heredicare 
select
    count(*) RecordsPerGroup,
    consensus_class,
    protein_class
from 
(SELECT 
	variant_id, 
	consensus_class, 
	(SELECT classification_protein FROM automatic_classification WHERE automatic_classification.variant_id = variant_heredicare_annotation.variant_id) as protein_class 
FROM variant_heredicare_annotation
)s
group by consensus_class,protein_class
