



/* create users 
CREATE USER 'HerediVar_superuser'@'%' IDENTIFIED BY '20220303s' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_annotation'@'%' IDENTIFIED BY '20220303a' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_user'@'%' IDENTIFIED BY '20220303u' PASSWORD EXPIRE NEVER;
*/



/* grant priviliges to annotation user */
GRANT SELECT, INSERT, UPDATE ON HerediVar.variant_annotation TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar.variant_literature TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar.variant_consequence TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.annotation_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.gene TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.transcript TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar.variant TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.task_force_protein_domains TO 'HerediVar_annotation';
GRANT SELECT, UPDATE ON HerediVar.annotation_queue TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar.clinvar_variant_annotation TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar.clinvar_submission TO 'HerediVar_annotation';
GRANT INSERT ON HerediVar.heredicare_center_classification TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar.variant_ids TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.pfam_id_mapping TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.pfam_legacy TO 'HerediVar_annotation';

/* grant priviliges to standard user */
GRANT SELECT, INSERT, UPDATE ON HerediVar.user TO 'HerediVar_user';
GRANT SELECT ON HerediVar.* TO 'HerediVar_user';
GRANT INSERT ON HerediVar.assay TO 'HerediVar_user';
GRANT INSERT, DELETE ON HerediVar.list_variants TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar.user_classification TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar.user_classification_criteria_applied TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar.user_variant_lists TO 'HerediVar_user';
GRANT INSERT ON HerediVar.variant TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar.annotation_queue TO 'HerediVar_user';


/* grant priviliges to super user */
GRANT SELECT, INSERT, UPDATE ON HerediVar.user TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.* TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar.assay TO 'HerediVar_superuser';
GRANT INSERT, DELETE ON HerediVar.list_variants TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar.user_classification TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar.user_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar.user_variant_lists TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar.variant TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar.annotation_queue TO 'HerediVar_superuser';

GRANT INSERT, UPDATE ON HerediVar.variant_ids TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar.consensus_classification TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar.consensus_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar.import_queue TO 'HerediVar_superuser';




