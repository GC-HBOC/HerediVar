ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `source` `source` ENUM('heredicare', 'vcf', 'heredicare_complete', 'heredicare_specific') NOT NULL DEFAULT 'heredicare' ;

UPDATE import_queue SET source = 'heredicare_complete' WHERE source = 'heredicare';

ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `source` `source` ENUM('vcf', 'heredicare_complete', 'heredicare_specific') NOT NULL DEFAULT 'heredicare_complete' ;


SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE table variant_cancerhotspots_annotation; 
SET FOREIGN_KEY_CHECKS = 1;

DELETE FROM variant_annotation WHERE annotation_type_id IN (
SELECT id FROM annotation_type WHERE title IN ("cancerhotspots", "cancerhotspots_ac", "cancerhotspots_af")
);

DELETE FROM variant_ids WHERE annotation_type_id = (SELECT id FROM annotation_type WHERE display_title = 'cosmic-id')
