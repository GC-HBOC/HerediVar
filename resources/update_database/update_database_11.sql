ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `source` `source` ENUM('heredicare', 'vcf', 'heredicare_complete', 'heredicare_specific') NOT NULL DEFAULT 'heredicare' ;

UPDATE import_queue SET source = 'heredicare_complete' WHERE source = 'heredicare';

ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `source` `source` ENUM('vcf', 'heredicare_complete', 'heredicare_specific') NOT NULL DEFAULT 'heredicare_complete' ;
