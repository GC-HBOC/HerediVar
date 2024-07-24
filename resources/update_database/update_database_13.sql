INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('heredicare_vid', 'HerediCare VID', 'The VID from HerediCare.The version_date is inaccurate. They are always up to date when reimporting from heredicare.', 'int', '-', '2024-07-24', 'ID', '0', '0');


ALTER TABLE `HerediVar`.`import_queue` 
CHANGE COLUMN `source` `source` ENUM('vcf', 'heredicare_complete', 'heredicare_specific', 'heredicare_update') NOT NULL DEFAULT 'heredicare_complete' ;

UPDATE `HerediVar`.`import_queue` SET source = 'heredicare_update' WHERE source = 'heredicare_complete';