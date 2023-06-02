



/* create users
CREATE DATABASE HerediVar CHARACTER SET = utf8 COLLATE = utf8_general_ci;
CREATE USER 'HerediVar_superuser'@'%' IDENTIFIED BY '20220303s' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_annotation'@'%' IDENTIFIED BY '20220303a' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_user'@'%' IDENTIFIED BY '20220303u' PASSWORD EXPIRE NEVER;
CREATE USER 'HerediVar_read_only'@'%' IDENTIFIED BY '20220303r' PASSWORD EXPIRE NEVER;
*/



/* grant priviliges to annotation user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1_test.variant_annotation TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1_test.variant_literature TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar_ahdoebm1_test.variant_consequence TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.annotation_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.gene TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.transcript TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar_ahdoebm1_test.variant TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.task_force_protein_domains TO 'HerediVar_annotation';
GRANT SELECT, UPDATE ON HerediVar_ahdoebm1_test.annotation_queue TO 'HerediVar_annotation';
GRANT SELECT, INSERT, DELETE ON HerediVar_ahdoebm1_test.clinvar_variant_annotation TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1_test.clinvar_submission TO 'HerediVar_annotation';
GRANT INSERT ON HerediVar_ahdoebm1_test.heredicare_center_classification TO 'HerediVar_annotation';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1_test.variant_ids TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.pfam_id_mapping TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.pfam_legacy TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1_test.gene_alias TO 'HerediVar_annotation';

/* grant priviliges to standard user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1_test.user TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1_test.* TO 'HerediVar_user';
GRANT INSERT ON HerediVar_ahdoebm1_test.assay TO 'HerediVar_user';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1_test.list_variants TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.user_classification TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_classification_criteria_applied TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_variant_lists TO 'HerediVar_user';
GRANT INSERT ON HerediVar_ahdoebm1_test.variant TO 'HerediVar_user';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.annotation_queue TO 'HerediVar_user';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_classification_selected_literature TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1_test.gene_alias TO 'HerediVar_user';

/* grant priviliges to super user */
GRANT SELECT, INSERT, UPDATE ON HerediVar_ahdoebm1_test.user TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1_test.* TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1_test.assay TO 'HerediVar_superuser';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1_test.list_variants TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.user_classification TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_variant_lists TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1_test.variant TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.annotation_queue TO 'HerediVar_superuser';

GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.variant_ids TO 'HerediVar_superuser';
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.consensus_classification TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1_test.consensus_classification_criteria_applied TO 'HerediVar_superuser';
GRANT INSERT ON HerediVar_ahdoebm1_test.import_queue TO 'HerediVar_superuser';

GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_classification_selected_literature TO 'HerediVar_superuser';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.consensus_classification_selected_literature TO 'HerediVar_superuser';

GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.heredivar_clinvar_submissions TO 'HerediVar_superuser';

GRANT SELECT ON HerediVar_ahdoebm1_test.gene_alias TO 'HerediVar_superuser';

/* grant priviliges to read only user */
GRANT SELECT, SHOW VIEW ON HerediVar_ahdoebm1_test.* TO 'HerediVar_read_only';
/*GRANT SELECT, SHOW VIEW ON HerediVar_ahdoebm1_test.* TO 'HerediVar_read_only';*/
GRANT INSERT, UPDATE ON HerediVar_ahdoebm1_test.user TO 'HerediVar_read_only';
GRANT INSERT, DELETE ON HerediVar_ahdoebm1_test.list_variants TO 'HerediVar_read_only';
GRANT INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1_test.user_variant_lists TO 'HerediVar_read_only';
GRANT SELECT ON HerediVar_ahdoebm1_test.gene_alias TO 'HerediVar_read_only';