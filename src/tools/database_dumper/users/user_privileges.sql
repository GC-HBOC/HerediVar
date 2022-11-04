



/* create users 
CREATE USER 'HerediVar_superuser'@'%' IDENTIFIED BY '20220303s' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_annotation'@'%' IDENTIFIED BY '20220303a' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_user'@'%' IDENTIFIED BY '20220303u' PASSWORD EXPIRE NEVER;
*/

/* grant priviliges to annotation user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1.variant_annotation TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1.variant_literature TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1.variant_consequence TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.annotation_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.gene TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.transcript TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar_ahdoebm1.variant TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.task_force_protein_domains TO 'HerediVar_annotation';
GRANT SELECT, UPDATE ON HerediVar_ahdoebm1.annotation_queue TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar_ahdoebm1.clinvar_variant_annotation TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1.clinvar_submission TO 'HerediVar_annotation';
GRANT INSERT ON HerediVar_ahdoebm1.heredicare_center_classification TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.pfam_id_mapping TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.pfam_legacy TO 'HerediVar_annotation';

/* grant priviliges to standard user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1.user TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.* TO 'HerediVar_user';
GRANT INSERT ON HerediVar_ahdoebm1.assay TO 'HerediVar_user';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1.list_variants TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.user_classification TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.user_classification_criteria_applied TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.user_variant_lists TO 'HerediVar_user';
GRANT INSERT ON HerediVar_ahdoebm1.variant TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.annotation_queue TO 'HerediVar_user';


/* grant priviliges to super user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1.user TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.* TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1.assay TO 'HerediVar_superuser';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1.list_variants TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.user_classification TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.user_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.user_variant_lists TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1.variant TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.annotation_queue TO 'HerediVar_superuser';

GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1.consensus_classification TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1.consensus_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1.import_queue TO 'HerediVar_superuser';




